from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ChallengeLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class Framework(str, Enum):
    streamlit = "streamlit"
    gradio = "gradio"
    shiny = "shiny"
    panel = "panel"
    dash = "dash"


class GeneratedAppSpec(BaseModel):
    """Structured output extracted from the model."""

    code: str = Field(..., description="Full app source code (preferably single-file).")
    run_command: str = Field(
        ...,
        description="Shell command to run the app locally from its directory.",
    )
    requirements_txt: str = Field(
        ..., description="Contents of requirements.txt needed to run the app."
    )
    instructions: str = Field(
        ..., description="Any extra setup/run notes (ports, env vars, etc.)."
    )


class Gate1Result(BaseModel):
    ok: bool
    error: str | None = None


class Gate2Result(BaseModel):
    ok: bool
    url: str | None = None
    screenshot_path: str | None = None
    screenshot_before_path: str | None = None
    screenshot_after_path: str | None = None
    error: str | None = None
    skipped_reason: str | None = None


class Gate3Result(BaseModel):
    ok: bool
    passed: bool | None = None
    solver_answer: str | None = None
    grader_score: str | None = None
    grader_explanation: str | None = None
    inspect_log: str | None = None
    error: str | None = None
    skipped_reason: str | None = None


class EvalResult(BaseModel):
    framework: Framework
    level: ChallengeLevel
    model_id: str
    output_dir: str
    gate1: Gate1Result
    gate2: Gate2Result
    gate3: Gate3Result | None = None
