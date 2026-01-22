"""Gate 1 and Gate 2 evaluation functions."""

from __future__ import annotations

import logging
import os
import pathlib
import py_compile
import shlex
import signal
import subprocess
import time
from dataclasses import dataclass

import httpx
from playwright.sync_api import sync_playwright

from .config import get_framework_config
from .specs import Framework, Gate1Result, Gate2Result

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FrameworkRuntime:
    """Runtime configuration for a framework app."""

    url: str
    command: list[str]
    supports_gate2: bool = True
    skip_reason: str | None = None
    startup_timeout_s: float = 60.0
    screenshot_delay_ms: int = 1500
    button_selector: str | None = None
    click_delay_ms: int = 1000


def _venv_bin(venv_dir: pathlib.Path, name: str) -> pathlib.Path:
    """Get path to a binary in the venv."""
    return venv_dir / "bin" / name


def gate1_compile(app_path: pathlib.Path) -> Gate1Result:
    """Gate 1: Check if the Python code compiles without syntax errors."""
    try:
        py_compile.compile(str(app_path), doraise=True)
        logger.debug("Gate 1 passed for %s", app_path)
        return Gate1Result(ok=True)
    except Exception as e:  # noqa: BLE001
        logger.warning("Gate 1 failed for %s: %s", app_path, e)
        return Gate1Result(ok=False, error=f"{type(e).__name__}: {e}")


def _wait_for_200(
    url: str,
    timeout_s: float = 60.0,
    interval_s: float = 0.5,
) -> None:
    """Wait for the server to respond with HTTP 200."""
    deadline = time.time() + timeout_s
    last_err: Exception | None = None

    logger.debug("Waiting for %s (timeout: %.1fs)", url, timeout_s)

    with httpx.Client(timeout=2.5) as client:
        while time.time() < deadline:
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    logger.debug("Got 200 OK from %s", url)
                    return
            except Exception as e:  # noqa: BLE001
                last_err = e
            time.sleep(interval_s)

    if last_err is None:
        raise TimeoutError(f"Timed out waiting for 200 OK: {url}")
    raise TimeoutError(f"Timed out waiting for 200 OK: {url}. Last error: {last_err}")


def _take_screenshot(
    url: str,
    out_path: pathlib.Path,
    timeout_ms: int = 60_000,
    delay_ms: int = 1500,
    button_selector: str | None = None,
    click_delay_ms: int = 1000,
) -> None:
    """Take a screenshot of the page using Playwright."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug("Taking screenshot of %s", url)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        page.wait_for_timeout(delay_ms)
        if button_selector:
            try:
                page.locator(button_selector).first.click(timeout=timeout_ms)
                page.wait_for_timeout(click_delay_ms)
            except Exception as e:  # noqa: BLE001
                logger.warning("Button click failed for %s: %s", url, e)
        page.screenshot(path=str(out_path), full_page=True)
        browser.close()

    logger.debug("Screenshot saved to %s", out_path)


def _build_framework_command(
    framework: Framework,
    host: str,
    port: int,
    app_dir: pathlib.Path,
    venv_dir: pathlib.Path,
) -> list[str]:
    """Build the command to run a framework app."""
    python = _venv_bin(venv_dir, "python")
    app_file = app_dir / "app.py"

    if framework == Framework.streamlit:
        return [
            str(python),
            "-m",
            "streamlit",
            "run",
            str(app_file),
            "--server.headless",
            "true",
            "--server.address",
            host,
            "--server.port",
            str(port),
            "--browser.gatherUsageStats",
            "false",
        ]

    if framework == Framework.shiny:
        shiny = _venv_bin(venv_dir, "shiny")
        return [
            str(shiny),
            "run",
            "--host",
            host,
            "--port",
            str(port),
            str(app_file),
        ]

    if framework == Framework.panel:
        panel = _venv_bin(venv_dir, "panel")
        return [
            str(panel),
            "serve",
            str(app_file),
            "--address",
            host,
            "--port",
            str(port),
            "--allow-websocket-origin",
            f"{host}:{port}",
            "--show",
            "false",
        ]

    if framework == Framework.gradio:
        return [str(python), str(app_file)]

    if framework == Framework.dash:
        return [str(python), str(app_file)]

    return ["true"]  # No-op for unsupported frameworks


def _framework_runtime(
    *,
    framework: Framework,
    host: str,
    port: int,
    app_dir: pathlib.Path,
    venv_dir: pathlib.Path,
) -> FrameworkRuntime:
    """Create runtime configuration for a framework."""
    config = get_framework_config(framework)

    # Build base URL with framework-specific suffix (Panel serves at /app)
    base_url = f"http://{host}:{port}"
    url = f"{base_url}{config.url_suffix}"

    cmd = _build_framework_command(
        framework=framework,
        host=host,
        port=port,
        app_dir=app_dir,
        venv_dir=venv_dir,
    )

    if cmd == ["true"]:
        return FrameworkRuntime(
            url=url,
            command=cmd,
            supports_gate2=False,
            skip_reason=f"Framework {framework.value} not supported for Gate 2.",
        )

    return FrameworkRuntime(
        url=url,
        command=cmd,
        startup_timeout_s=config.startup_timeout_s,
        screenshot_delay_ms=config.screenshot_delay_ms,
        button_selector=config.button_selector,
        click_delay_ms=config.click_delay_ms,
    )


def _create_venv(venv_dir: pathlib.Path) -> pathlib.Path:
    """Create a virtual environment using uv."""
    venv_dir.parent.mkdir(parents=True, exist_ok=True)
    if venv_dir.exists():
        logger.debug("Using existing venv at %s", venv_dir)
        return venv_dir

    logger.debug("Creating venv at %s", venv_dir)
    subprocess.check_call(["uv", "venv", str(venv_dir)])
    return venv_dir


def _uv_install(
    venv_dir: pathlib.Path,
    requirements_path: pathlib.Path,
    extra_requirements: list[str] | None = None,
) -> None:
    """Install requirements using uv."""
    logger.debug("Installing requirements from %s", requirements_path)
    subprocess.check_call(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(_venv_bin(venv_dir, "python")),
            "-r",
            str(requirements_path),
        ]
    )
    if extra_requirements:
        logger.debug("Installing extra requirements: %s", extra_requirements)
        subprocess.check_call(
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(_venv_bin(venv_dir, "python")),
                *extra_requirements,
            ]
        )


def gate2_run_and_screenshot(
    *,
    framework: Framework,
    app_dir: pathlib.Path,
    host: str,
    port: int,
    screenshot_path: pathlib.Path,
    timeout_s: float | None = None,
) -> Gate2Result:
    """Gate 2: Run the app and take before/after screenshots.

    Args:
        framework: The framework to run
        app_dir: Directory containing app.py and requirements.txt
        host: Host to bind the app to
        port: Port to bind the app to
        screenshot_path: Base path for screenshots
        screenshots: Captures before and after clicking a button
        click: Attempts first button click
        timeout_s: Override timeout (uses framework default if None)

    Returns:
        Gate2Result with success status and screenshot paths
    """
    # Resolve to absolute paths
    app_dir = app_dir.resolve()
    screenshot_path = screenshot_path.resolve()
    screenshot_before = screenshot_path.with_name(
        f"{screenshot_path.stem}_before{screenshot_path.suffix}"
    )
    screenshot_after = screenshot_path.with_name(
        f"{screenshot_path.stem}_after{screenshot_path.suffix}"
    )
    venv_dir = app_dir / ".venv"

    runtime = _framework_runtime(
        framework=framework,
        host=host,
        port=port,
        app_dir=app_dir,
        venv_dir=venv_dir,
    )
    runtime_extra_requirements = get_framework_config(framework).extra_requirements

    if not runtime.supports_gate2:
        return Gate2Result(
            ok=False,
            skipped_reason=runtime.skip_reason,
        )

    # Use provided timeout or framework default
    effective_timeout = timeout_s or runtime.startup_timeout_s

    logger.info(
        "Running Gate 2 for %s at %s (timeout: %.1fs)",
        framework.value,
        runtime.url,
        effective_timeout,
    )

    try:
        _create_venv(venv_dir)
        _uv_install(
            venv_dir,
            app_dir / "requirements.txt",
            extra_requirements=runtime_extra_requirements,
        )

        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")

        logger.debug("Starting app: %s", " ".join(runtime.command))

        proc = subprocess.Popen(
            runtime.command,
            cwd=str(app_dir),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        try:
            _wait_for_200(runtime.url, timeout_s=effective_timeout)
            _take_screenshot(
                runtime.url,
                screenshot_before,
                delay_ms=runtime.screenshot_delay_ms,
            )
            if runtime.button_selector:
                _take_screenshot(
                    runtime.url,
                    screenshot_after,
                    delay_ms=runtime.screenshot_delay_ms,
                    button_selector=runtime.button_selector,
                    click_delay_ms=runtime.click_delay_ms,
                )
            else:
                _take_screenshot(
                    runtime.url,
                    screenshot_after,
                    delay_ms=runtime.screenshot_delay_ms,
                )
            logger.info("Gate 2 passed for %s", framework.value)
            return Gate2Result(
                ok=True,
                url=runtime.url,
                screenshot_path=str(screenshot_path),
                screenshot_before_path=str(screenshot_before),
                screenshot_after_path=str(screenshot_after),
            )
        finally:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()

    except Exception as e:  # noqa: BLE001
        logger.error("Gate 2 failed for %s: %s", framework.value, e)
        return Gate2Result(
            ok=False,
            url=runtime.url,
            error=f"{type(e).__name__}: {e}",
            screenshot_before_path=str(screenshot_before),
            screenshot_after_path=str(screenshot_after),
        )


def parse_run_command(run_command: str) -> list[str]:
    """Parse a run command string into a list of arguments."""
    return shlex.split(run_command)
