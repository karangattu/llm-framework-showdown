from __future__ import annotations

import json
import pathlib
from datetime import datetime

from rich.console import Console

from .chat_generate import GenerationJob, generate_apps_sync
from .gates import gate1_compile, gate2_run_and_screenshot
from .specs import (
    ChallengeLevel,
    EvalResult,
    Framework,
    Gate1Result,
    Gate2Result,
    Gate3Result,
)


console = Console()


def _safe_dir_name(value: str) -> str:
    cleaned = "".join(c for c in value if c.isalnum() or c in ("-", "_", "."))
    return cleaned.strip(".")


def _write_text(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_evaluation(
    *,
    frameworks: list[Framework],
    levels: list[ChallengeLevel],
    model_ids: list[str],
    out_dir: pathlib.Path,
    host: str = "127.0.0.1",
    base_port: int = 8501,
    aws_region: str | None = None,
    aws_profile: str | None = None,
    max_active: int = 4,
    gate2: bool = True,
    gate3: bool = False,
    gate3_grader_model: str | None = None,
    gate3_log_dir: pathlib.Path | None = None,
    gate3_max_samples: int | None = None,
) -> list[EvalResult]:
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs: list[GenerationJob] = []
    job_meta: list[tuple[Framework, ChallengeLevel, int]] = []
    port = base_port
    for framework in frameworks:
        for level in levels:
            jobs.append(
                GenerationJob(
                    framework=framework,
                    level=level,
                    host=host,
                    port=port,
                )
            )
            job_meta.append((framework, level, port))
            port += 1

    all_results: list[EvalResult] = []

    for model_id in model_ids:
        console.rule(f"Model: {model_id}")
        model_results: list[EvalResult] = []
        gen_results = generate_apps_sync(
            model_id=model_id,
            jobs=jobs,
            aws_region=aws_region,
            aws_profile=aws_profile,
            max_active=max_active,
        )

        for (framework, level, job_port), item in zip(
            job_meta, gen_results, strict=False
        ):
            model_slug = _safe_dir_name(model_id)
            job_dir = out_dir / framework.value / level.value / model_slug
            job_dir.mkdir(parents=True, exist_ok=True)

            if isinstance(item, Exception):
                result = EvalResult(
                    framework=framework,
                    level=level,
                    model_id=model_id,
                    output_dir=str(job_dir),
                    gate1=Gate1Result(
                        ok=False,
                        error=f"generation failed: {item}",
                    ),
                    gate2=Gate2Result(ok=False, error="generation failed"),
                )
                all_results.append(result)
                model_results.append(result)
                continue

            if item is None:
                result = EvalResult(
                    framework=framework,
                    level=level,
                    model_id=model_id,
                    output_dir=str(job_dir),
                    gate1=Gate1Result(
                        ok=False,
                        error="generation was not submitted",
                    ),
                    gate2=Gate2Result(
                        ok=False,
                        error="generation was not submitted",
                    ),
                )
                all_results.append(result)
                model_results.append(result)
                continue

            spec = item.data

            _write_text(job_dir / "app.py", spec.code)
            _write_text(job_dir / "requirements.txt", spec.requirements_txt)
            _write_text(job_dir / "INSTRUCTIONS.md", spec.instructions)
            _write_text(job_dir / "RUN_COMMAND.txt", spec.run_command)

            gate1 = gate1_compile(job_dir / "app.py")
            screenshot_path = job_dir / "dashboard.png"
            if gate2:
                gate2_result = gate2_run_and_screenshot(
                    framework=framework,
                    app_dir=job_dir,
                    host=host,
                    port=job_port,
                    screenshot_path=screenshot_path,
                )
            else:
                gate2_result = Gate2Result(
                    ok=False,
                    skipped_reason="Gate 2 disabled",
                )

            result = EvalResult(
                framework=framework,
                level=level,
                model_id=model_id,
                output_dir=str(job_dir),
                gate1=gate1,
                gate2=gate2_result,
            )
            all_results.append(result)
            model_results.append(result)

            console.print(
                (
                    f"[{framework.value}/{level.value}] "
                    f"gate1={gate1.ok} "
                    f"gate2={getattr(gate2_result, 'ok', False)}"
                )
            )

        if gate3:
            if not gate3_grader_model:
                raise ValueError(
                    "gate3_grader_model is required when gate3=True "
                    "(pass --gate3-grader-model ...)"
                )

            try:
                from .gate3_inspect import Gate3Case, gate3_grade_screenshots
            except Exception as e:  # noqa: BLE001
                for r in model_results:
                    r.gate3 = Gate3Result(
                        ok=False,
                        error=f"Gate 3 import failed: {e}",
                    )
                continue

            cases: list[Gate3Case] = []
            for r in model_results:
                if not r.gate2.ok:
                    r.gate3 = Gate3Result(
                        ok=False,
                        skipped_reason="Gate 2 did not produce screenshots",
                    )
                    continue

                screenshot_before = pathlib.Path(r.output_dir) / "dashboard_before.png"
                screenshot_after = pathlib.Path(r.output_dir) / "dashboard_after.png"
                if not screenshot_before.exists():
                    r.gate3 = Gate3Result(
                        ok=False,
                        error=f"Screenshot missing: {screenshot_before}",
                    )
                    continue
                if not screenshot_after.exists():
                    r.gate3 = Gate3Result(
                        ok=False,
                        error=f"Screenshot missing: {screenshot_after}",
                    )
                    continue

                cases.append(
                    Gate3Case(
                        framework=r.framework,
                        level=r.level,
                        model_id=r.model_id,
                        output_dir=pathlib.Path(r.output_dir),
                        screenshot_before_path=screenshot_before,
                        screenshot_after_path=screenshot_after,
                    )
                )

            if not cases:
                continue

            try:
                max_samples = gate3_max_samples
                if max_samples is None:
                    max_samples = len(cases)

                gate3_by_dir = gate3_grade_screenshots(
                    cases=cases,
                    solver_model_id=model_id,
                    grader_model=gate3_grader_model,
                    aws_region=aws_region,
                    aws_profile=aws_profile,
                    log_dir=gate3_log_dir,
                    max_samples=max_samples,
                )

                for r in model_results:
                    if r.output_dir in gate3_by_dir:
                        r.gate3 = gate3_by_dir[r.output_dir]
                        continue
                    if r.gate3 is None:
                        r.gate3 = Gate3Result(
                            ok=False,
                            error="No Gate 3 result produced for this case",
                        )
            except Exception as e:  # noqa: BLE001
                for r in model_results:
                    if r.gate3 is None:
                        r.gate3 = Gate3Result(
                            ok=False,
                            error=f"Gate 3 failed: {e}",
                        )

    summary_path = out_dir / (
        f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    summary_path.write_text(
        json.dumps([r.model_dump() for r in all_results], indent=2),
        encoding="utf-8",
    )
    console.print(f"Wrote summary: {summary_path}")

    return all_results
