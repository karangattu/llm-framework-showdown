"""
Inspect AI evaluation: Score LLM-generated tip calculator apps.

Uses claude-sonnet-4-6 as a model-graded scorer to evaluate the generated
apps across 3 criteria: maintainability, readability, and requirement adherence.
Each sample includes the app code plus before/after screenshots.

Run:
    inspect eval eval_apps.py --model anthropic/claude-sonnet-4-6
"""

import re
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import MemoryDataset, Sample
from inspect_ai.model import (
    ChatMessageUser,
    ContentImage,
    ContentText,
)
from inspect_ai.scorer import (
    Score,
    mean,
    scorer,
    stderr,
)
from inspect_ai.solver import generate, system_message

BASE_DIR = Path(__file__).parent

FRAMEWORKS = {
    "Streamlit": "streamlit",
    "Plotly Dash": "dash",
    "Panel": "panel",
    "Shiny for Python": "shiny",
}

ORIGINAL_PROMPT = (
    "Create an app using {framework} that is a basic tip calculator which "
    "features a clean interface with input fields for the bill amount and "
    "tip percentage (with 15%, 18%, or 20% presets). It must instantly "
    "calculate and display the tip amount and the total bill (bill + tip), "
    "with an optional, useful feature to split the total among multiple "
    "people. Do not use extra packages or CSS or JavaScript other than what "
    "{framework} already provides."
)

SYSTEM_PROMPT = """\
You are an expert code reviewer and UI/UX evaluator. You will be given:
1. The source code of a Python web app built with a specific framework.
2. A "before" screenshot showing the app in its default/initial state.
3. An "after" screenshot showing the app after a user entered a bill of \
$85.50, selected 20% tip, and split among 3 people.

You must evaluate the app on THREE criteria, each scored 1-10:

**Criterion 1: Maintainability** (1-10)
- Is the code well-structured and modular?
- Would it be easy to extend or modify in the future?
- Are there clear variable names and logical organization?

**Criterion 2: Readability** (1-10)
- Is the code intuitive to read and understand?
- Is it well-commented or self-documenting?
- Does it follow idiomatic patterns for the framework?

**Criterion 3: Requirement Adherence** (1-10)
- Does it have input fields for bill amount and tip percentage?
- Does it have 15%, 18%, and 20% tip presets?
- Does it instantly calculate and display tip amount and total bill?
- Does it support splitting the total among multiple people?
- Does it avoid extra packages, CSS, or JavaScript beyond the framework?
- Do the before/after screenshots confirm the app works as specified?

After your analysis, you MUST end your response with exactly these three \
lines (scores as integers 1-10):

MAINTAINABILITY_SCORE: <score>
READABILITY_SCORE: <score>
ADHERENCE_SCORE: <score>
"""

EVAL_PROMPT_TEMPLATE = """\
## Framework: {framework}

### Original prompt given to the LLM that generated this app:
{original_prompt}

### Generated app code ({framework}):
```python
{code}
```

Below are the before and after screenshots of the running app.
The "before" screenshot shows the app right after launch (default state).
The "after" screenshot shows the app after entering: bill = $85.50, \
tip = 20%, split among 3 people.

Please evaluate this app on the three criteria \
(Maintainability, Readability, Requirement Adherence) and provide your scores.
"""


def _build_samples() -> list[Sample]:
    """Build one Sample per framework with code + before/after images."""
    samples = []
    for framework, dirname in FRAMEWORKS.items():
        app_dir = BASE_DIR / dirname
        code_path = app_dir / "app.py"
        before_path = app_dir / "before.png"
        after_path = app_dir / "after.png"

        if not code_path.exists():
            continue

        code = code_path.read_text(encoding="utf-8")
        original_prompt = ORIGINAL_PROMPT.format(framework=framework)

        eval_text = EVAL_PROMPT_TEMPLATE.format(
            framework=framework,
            original_prompt=original_prompt,
            code=code,
        )

        content: list = [ContentText(text=eval_text)]

        if before_path.exists():
            content.append(
                ContentText(text="\n### Before screenshot (default state):")
            )
            content.append(ContentImage(image=str(before_path)))

        if after_path.exists():
            content.append(
                ContentText(
                    text="\n### After screenshot "
                    "(bill=$85.50, tip=20%, split=3):"
                )
            )
            content.append(ContentImage(image=str(after_path)))

        samples.append(
            Sample(
                input=[ChatMessageUser(content=content)],
                target="Evaluate the app on all three criteria.",
                id=dirname,
                metadata={"framework": framework},
            )
        )

    return samples


@scorer(
    metrics={
        "maintainability": [mean(), stderr()],
        "readability": [mean(), stderr()],
        "adherence": [mean(), stderr()],
    }
)
def criteria_scorer():
    """Extract the three criterion scores from model output."""

    async def score(state, target):
        completion = state.output.completion

        maintainability = _extract_score(
            completion, "MAINTAINABILITY_SCORE"
        )
        readability = _extract_score(completion, "READABILITY_SCORE")
        adherence = _extract_score(completion, "ADHERENCE_SCORE")

        return Score(
            value={
                "maintainability": maintainability,
                "readability": readability,
                "adherence": adherence,
            },
            explanation=completion,
        )

    return score


def _extract_score(text: str, label: str) -> float:
    """Extract a numeric score for a given label from model output."""
    pattern = rf"{label}:\s*(\d+(?:\.\d+)?)"
    match = re.search(pattern, text)
    if match:
        return min(max(float(match.group(1)), 1.0), 10.0)
    return 0.0


@task
def framework_eval():
    """Evaluate LLM-generated tip calculator apps across frameworks."""
    return Task(
        dataset=MemoryDataset(_build_samples()),
        solver=[
            system_message(SYSTEM_PROMPT),
            generate(),
        ],
        scorer=criteria_scorer(),
    )
