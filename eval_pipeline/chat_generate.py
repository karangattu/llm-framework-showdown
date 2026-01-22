"""Code generation using ChatBedrockAnthropic."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

from rich.progress import Progress, SpinnerColumn, TextColumn

import chatlas as ctl

from .prompts import build_generation_prompt
from .specs import ChallengeLevel, Framework, GeneratedAppSpec

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GenerationJob:
    """A single code generation job."""

    framework: Framework
    level: ChallengeLevel
    host: str
    port: int


@dataclass
class GenerationResult:
    """Result wrapper for generated app specification."""

    data: GeneratedAppSpec


def make_chat(
    *,
    model_id: str,
    aws_region: str | None,
    aws_profile: str | None,
) -> ctl.Chat:
    """Create a ChatBedrockAnthropic instance."""
    return ctl.ChatBedrockAnthropic(
        model=model_id,
        aws_region=aws_region,
        aws_profile=aws_profile,
    )


def _parse_response(text: str) -> GeneratedAppSpec:
    """Parse model response to extract structured fields.

    Attempts multiple parsing strategies in order:
    1. Direct JSON parsing
    2. JSON in markdown code block
    3. JSON object anywhere in text
    4. Fallback to defaults
    """
    # Strategy 1: Direct JSON
    try:
        data = json.loads(text.strip())
        logger.debug("Parsed response as direct JSON")
        return GeneratedAppSpec(**data)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Strategy 2: JSON in markdown code block
    try:
        json_match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            logger.debug("Parsed response from markdown code block")
            return GeneratedAppSpec(**data)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Strategy 3: JSON object anywhere in text
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            logger.debug("Parsed response from embedded JSON")
            return GeneratedAppSpec(**data)
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # Strategy 4: Fallback
    logger.warning("Failed to parse model response, using fallback")
    return GeneratedAppSpec(
        code="# Failed to parse response",
        run_command="python app.py",
        requirements_txt="",
        instructions="Failed to parse model response.",
    )


def generate_single_app(
    *,
    model_id: str,
    job: GenerationJob,
    aws_region: str | None = None,
    aws_profile: str | None = None,
) -> GenerationResult:
    """Generate a single app from a job specification."""
    chat = make_chat(
        model_id=model_id,
        aws_region=aws_region,
        aws_profile=aws_profile,
    )

    prompt = build_generation_prompt(
        framework=job.framework,
        level=job.level,
        host=job.host,
        port=job.port,
    )

    logger.info(
        "Generating %s/%s app on port %d",
        job.framework.value,
        job.level.value,
        job.port,
    )

    response = chat.chat(prompt)
    response_text = str(response)
    spec = _parse_response(response_text)

    return GenerationResult(data=spec)


def generate_apps_sync(
    *,
    model_id: str,
    jobs: list[GenerationJob],
    aws_region: str | None = None,
    aws_profile: str | None = None,
    max_active: int = 4,  # noqa: ARG001 - kept for API compatibility
    show_progress: bool = True,
) -> list[Any]:
    """Generate apps sequentially using ChatBedrockAnthropic.

    Args:
        model_id: Bedrock model identifier
        jobs: List of generation jobs
        aws_region: AWS region for Bedrock
        aws_profile: AWS profile name
        max_active: Unused, kept for API compatibility
        show_progress: Whether to show progress bar

    Returns:
        List of GenerationResult or Exception for each job
    """
    results: list[Any] = []

    if show_progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task("Generating apps...", total=len(jobs))

            for job in jobs:
                progress.update(
                    task,
                    description=f"Generating {job.framework.value}/{job.level.value}",
                )
                try:
                    result = generate_single_app(
                        model_id=model_id,
                        job=job,
                        aws_region=aws_region,
                        aws_profile=aws_profile,
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(
                        "Generation failed for %s/%s: %s",
                        job.framework.value,
                        job.level.value,
                        e,
                    )
                    results.append(e)
                progress.advance(task)
    else:
        for job in jobs:
            try:
                result = generate_single_app(
                    model_id=model_id,
                    job=job,
                    aws_region=aws_region,
                    aws_profile=aws_profile,
                )
                results.append(result)
            except Exception as e:
                logger.error(
                    "Generation failed for %s/%s: %s",
                    job.framework.value,
                    job.level.value,
                    e,
                )
                results.append(e)

    return results
