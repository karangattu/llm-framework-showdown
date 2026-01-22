"""Configuration and framework registry for the eval pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .specs import Framework

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FrameworkConfig:
    """Configuration for a specific framework."""

    name: str
    startup_timeout_s: float = 60.0
    screenshot_delay_ms: int = 1500
    url_suffix: str = ""
    click_delay_ms: int = 1000
    requires_bokeh: bool = False
    extra_requirements: list[str] = field(default_factory=list)


# Framework-specific configurations
FRAMEWORK_CONFIGS: dict[Framework, FrameworkConfig] = {
    Framework.streamlit: FrameworkConfig(
        name="streamlit",
        startup_timeout_s=60.0,
        screenshot_delay_ms=2000,
        click_delay_ms=1200,
    ),
    Framework.gradio: FrameworkConfig(
        name="gradio",
        startup_timeout_s=90.0,
        screenshot_delay_ms=2000,
        click_delay_ms=1200,
    ),
    Framework.shiny: FrameworkConfig(
        name="shiny",
        startup_timeout_s=90.0,
        screenshot_delay_ms=2000,
        click_delay_ms=1200,
    ),
    Framework.panel: FrameworkConfig(
        name="panel",
        startup_timeout_s=120.0,
        screenshot_delay_ms=3000,
        url_suffix="/app",
        click_delay_ms=2000,
        requires_bokeh=True,
        extra_requirements=["panel", "bokeh"],
    ),
    Framework.dash: FrameworkConfig(
        name="dash",
        startup_timeout_s=90.0,
        screenshot_delay_ms=2000,
        click_delay_ms=1200,
    ),
}


def get_framework_config(framework: Framework) -> FrameworkConfig:
    """Get configuration for a framework."""
    return FRAMEWORK_CONFIGS.get(
        framework,
        FrameworkConfig(name=framework.value),
    )


@dataclass
class EvalConfig:
    """Global evaluation configuration."""

    host: str = "127.0.0.1"
    base_port: int = 8501
    aws_region: str | None = None
    aws_profile: str | None = None
    max_active: int = 4
    default_timeout_s: float = 90.0
    enable_gate2: bool = True
    enable_gate3: bool = False
    gate3_grader_model: str | None = None
    gate3_log_dir: str | None = None
    gate3_max_samples: int | None = None
    verbose: bool = False

    def __post_init__(self) -> None:
        """Configure logging based on verbosity."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
