from __future__ import annotations

from .specs import ChallengeLevel, Framework


CHALLENGE_PROMPTS: dict[ChallengeLevel, str] = {
    ChallengeLevel.beginner: (
        "Create a [FRAMEWORK] app that displays a title 'My First App'. "
        "Include a text input field asking for a user's name and a button. "
        "When clicked, display a greeting message 'Hello, {name}!' "
        "below the button."
    ),
    ChallengeLevel.intermediate: (
        "Build a [FRAMEWORK] dashboard using the 'Penguins' dataset. "
        "It should have a sidebar with a dropdown to filter by 'Island'. "
        "The main area should display a scatter plot of Flipper Length vs. "
        "Body Mass, "
        "colored by Species. Ensure the plot updates when the filter changes."
    ),
    ChallengeLevel.advanced: (
        "Create a To-Do list application in [FRAMEWORK]. Users must be able "
        "to add tasks, "
        "mark them as 'Complete' (striking them through), and delete them. "
        "The list must persist in the session state so it doesn't vanish on "
        "page reload/interaction."
    ),
    ChallengeLevel.expert: (
        "Build a Real-Time Stock Ticker Monitor in [FRAMEWORK]. "
        "1. Use a dark theme custom CSS/Styling. "
        "2. Simulate a live feed updating a line chart every 1s. "
        "Avoid flicker. "
        "3. Include a 'Buy/Sell' control panel that logs transactions to a "
        "data table below the chart. "
        "4. Ensure the layout is responsive (mobile-friendly)."
    ),
}


def build_generation_prompt(
    *,
    framework: Framework,
    level: ChallengeLevel,
    host: str,
    port: int,
) -> str:
    task = CHALLENGE_PROMPTS[level].replace("[FRAMEWORK]", framework.value)

    framework_run_notes = {
        Framework.streamlit: (
            "Use Streamlit best practices. Do not use external files. "
            "The app must be runnable via Streamlit CLI."
        ),
        Framework.gradio: (
            "Use Gradio. The app should run via `python app.py` and must call "
            f'`launch(server_name="{host}", '
            f"server_port={port}, share=False)` for local hosting."
        ),
        Framework.shiny: (
            "Use Shiny for Python. Provide a single `app.py` for UI + server."
        ),
        Framework.panel: (
            "Use Panel (HoloViz). The app should run via `panel serve app.py`. "
            "Use `pn.extension()` at the top. Make the main component servable "
            "with `.servable()`. Do NOT use `pn.serve()` or `pn.panel().show()` "
            "since the app will be served via `panel serve`. "
            "Ensure there is at least one `pn.widgets.Button` with a click handler. "
            "Include 'panel' and 'bokeh' in requirements."
        ),
        Framework.dash: (
            "Use Plotly Dash. The app must run via `python app.py`. "
            "You MUST define `PORT = "
            f"{port}` and then call exactly: "
            f'`app.run(host="{host}", port=PORT, debug=False)`. '
            "Do not use `app.run_server`. Do not pick a different host. Do "
            "not ignore the provided PORT."
        ),
    }[framework]

    return "\n".join(
        [
            "You are an expert Python UI engineer.",
            "Generate a visually polished, modern dashboard-like app.",
            "Constraints:",
            "- Output must be valid Python.",
            "- Prefer a single file named `app.py`.",
            "- No placeholder pseudocode; everything must run.",
            "- Keep dependencies minimal.",
            f"- The app must bind to http://{host}:{port} (where applicable).",
            "- Avoid downloading large assets at runtime.",
            "",
            f"Framework-specific notes: {framework_run_notes}",
            "",
            f"TASK: {task}",
            "",
            "IMPORTANT: You MUST respond with ONLY a JSON object (no markdown, no extra text). Use this exact format:",
            '{"code": "<full app.py contents with escaped newlines as \\\\n>", "run_command": "<command>", "requirements_txt": "<package1\\npackage2>", "instructions": "<any extra steps>"}',
        ]
    )
