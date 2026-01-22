from __future__ import annotations

import os
import pathlib
import re
from dataclasses import dataclass

from .prompts import CHALLENGE_PROMPTS
from .specs import ChallengeLevel, Framework, Gate3Result


@dataclass(frozen=True)
class Gate3Case:
    framework: Framework
    level: ChallengeLevel
    model_id: str
    output_dir: pathlib.Path
    screenshot_before_path: pathlib.Path
    screenshot_after_path: pathlib.Path


_ANSWER_RE = re.compile(r"^\s*ANSWER\s*:\s*(PASS|FAIL)\s*$", re.IGNORECASE | re.M)


def _extract_answer(completion: str) -> str | None:
    match = _ANSWER_RE.search(completion or "")
    if not match:
        return None
    return match.group(1).upper()


def gate3_grade_screenshots(
    *,
    cases: list[Gate3Case],
    solver_model_id: str,
    grader_model: str,
    aws_region: str | None = None,
    aws_profile: str | None = None,
    log_dir: pathlib.Path | None = None,
    max_samples: int = 4,
) -> dict[str, Gate3Result]:
    """Run a single Inspect eval over multiple screenshots.

    Uses `solver=chat.to_solver()` (chatlas) to produce a PASS/FAIL verdict per
    screenshot, and `model_graded_qa` with a separate grader model to judge the
    verdict against the screenshot + rubric.

    Returns a mapping of `output_dir` (string) to Gate3Result.

    NOTE: This function imports inspect-ai + chatlas[eval] lazily so Gate 1/2
    run without those dependencies.
    """

    if not cases:
        return {}

    try:
        from chatlas import ChatBedrockAnthropic
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Gate 3 requires chatlas eval integration. "
            "Install with `pip install 'chatlas[eval]'`."
        ) from e

    try:
        from inspect_ai import Task, eval as inspect_eval
        from inspect_ai.dataset import MemoryDataset, Sample
        from inspect_ai.model import ChatMessageUser, ContentImage, ContentText
        from inspect_ai.scorer import model_graded_qa
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Gate 3 requires inspect-ai. Install with `pip install inspect-ai`."
        ) from e

    if aws_profile:
        os.environ.setdefault("AWS_PROFILE", aws_profile)
    if aws_region:
        os.environ.setdefault("AWS_DEFAULT_REGION", aws_region)

    if log_dir is None:
        log_dir = pathlib.Path("logs") / "gate3"
    log_dir.mkdir(parents=True, exist_ok=True)

    chat = ChatBedrockAnthropic(
        model=solver_model_id,
        aws_region=aws_region,
        aws_profile=aws_profile,
    )

    to_solver = getattr(chat, "to_solver", None)
    if to_solver is None:
        raise RuntimeError(
            "Gate 3 requires chatlas eval integration. "
            "Install with `pip install 'chatlas[eval]'`."
        )

    solver = to_solver()

    grader_instructions = "\n".join(
        [
            "You are a strict UI judge evaluating dashboard screenshots.",
            "Use the screenshots + task criterion to decide whether the answer "
            "is correct.",
            "Respond with exactly one of:",
            "GRADE: C  (correct)",
            "GRADE: I  (incorrect)",
            "Then add 1-2 short sentences explaining why.",
        ]
    )

    samples: list[Sample] = []
    for case in cases:
        if not case.screenshot_before_path.exists():
            continue
        if not case.screenshot_after_path.exists():
            continue

        task_text = CHALLENGE_PROMPTS[case.level].replace(
            "[FRAMEWORK]", case.framework.value
        )

        question = "\n".join(
            [
                "Decide whether the attached screenshots show a functional app",
                "that meets the TASK requirements and responds to the UI interaction.",
                "Return a verdict in this exact format:",
                "ANSWER: PASS|FAIL",
                "REASON: <one short sentence>",
                "",
                f"FRAMEWORK: {case.framework.value}",
                f"TASK: {task_text}",
                "NOTE: Screenshot 1 is before clicking, screenshot 2 is after.",
            ]
        )

        criterion = "\n".join(
            [
                "The solver's verdict must match what is visible in the screenshots.",
                "PASS only if the screenshots look like a working app UI and "
                "plausibly satisfy the TASK,",
                "including evidence that the button interaction updated the UI.",
                "FAIL if the screenshots show an error/traceback/blank page, "
                "or do not satisfy the TASK.",
            ]
        )

        user_msg = ChatMessageUser(
            content=[
                ContentText(text="Screenshot 1 (before click)"),
                ContentImage(image=str(case.screenshot_before_path)),
                ContentText(text="Screenshot 2 (after click)"),
                ContentImage(image=str(case.screenshot_after_path)),
                ContentText(text=question),
            ]
        )

        samples.append(
            Sample(
                id=str(case.output_dir),
                input=[user_msg],
                target=criterion,
                metadata={
                    "framework": case.framework.value,
                    "level": case.level.value,
                    "model_id": case.model_id,
                    "output_dir": str(case.output_dir),
                    "screenshot_before": str(case.screenshot_before_path),
                    "screenshot_after": str(case.screenshot_after_path),
                },
            )
        )

    if not samples:
        return {}

    task = Task(
        name="gate3_dashboard_screenshot",
        dataset=MemoryDataset(samples=samples, name="gate3_screenshots"),
        solver=solver,
        scorer=model_graded_qa(
            include_history=True,
            instructions=grader_instructions,
            model=grader_model,
        ),
    )

    logs = inspect_eval(
        task,
        model=None,
        log_dir=str(log_dir),
        log_format="json",
        log_images=True,
        max_samples=max_samples,
        fail_on_error=False,
    )

    if not logs:
        return {}

    log = logs[0]
    results: dict[str, Gate3Result] = {}

    for sample in log.samples or []:
        output_dir = str(sample.id)

        try:
            completion = sample.output.completion
        except Exception:  # noqa: BLE001
            completion = ""

        solver_answer = _extract_answer(completion)

        score = None
        if sample.scores:
            score = sample.scores.get("model_graded_qa")
            if score is None and len(sample.scores) == 1:
                score = next(iter(sample.scores.values()))

        if score is None:
            results[output_dir] = Gate3Result(
                ok=False,
                solver_answer=solver_answer,
                inspect_log=getattr(log, "location", None),
                error="No model_graded_qa score found on sample.",
            )
            continue

        if hasattr(score, "as_str"):
            grader_value = score.as_str()
        else:
            grader_value = str(score.value)
        grader_explanation = getattr(score, "explanation", None)

        passed: bool | None = None
        if grader_value == "C" and solver_answer in ("PASS", "FAIL"):
            passed = solver_answer == "PASS"

        results[output_dir] = Gate3Result(
            ok=True,
            passed=passed,
            solver_answer=solver_answer,
            grader_score=grader_value,
            grader_explanation=grader_explanation,
            inspect_log=getattr(log, "location", None),
        )

    return results
