"""
Generate tip calculator web apps for multiple Python frameworks using ChatAnthropic.

Uses chatlas with claude-sonnet-4-6 to generate a basic tip calculator app
for Streamlit, Plotly Dash, Panel, and Shiny for Python.

Prerequisites:
    - pip install "chatlas[anthropic]"
    - ANTHROPIC_API_KEY environment variable set
"""

import re
from pathlib import Path

from chatlas import ChatAnthropic

SYSTEM_PROMPT = (
    "You are an expert Python web developer. "
    "When asked to create an app, respond with ONLY the Python source code. "
    "Do not wrap the code in markdown code fences (no ```). "
    "Do not include any commentary, explanation, or text outside the code. "
    "Do not use any extra packages, CSS, or JavaScript beyond what the specified "
    "web framework already provides out of the box."
)

PROMPT_TEMPLATE = (
    "Create an app using {framework} that is a basic tip calculator which features "
    "a clean interface with input fields for the bill amount and tip percentage "
    "(with 15%, 18%, or 20% presets). It must instantly calculate and display the "
    "tip amount and the total bill (bill + tip), with an optional, useful feature "
    "to split the total among multiple people. "
    "Do not use extra packages or CSS or JavaScript other than what {framework} "
    "already provides."
)

FRAMEWORKS = {
    "Streamlit": "streamlit",
    "Plotly Dash": "dash",
    "Panel": "panel",
    "Shiny for Python": "shiny",
}


def strip_markdown_fences(code: str) -> str:
    """Remove accidental markdown code fences from LLM output."""
    code = re.sub(r"^```(?:python)?\s*\n", "", code)
    code = re.sub(r"\n```\s*$", "", code)
    return code.strip()


def generate_app(framework: str) -> str:
    """Generate a tip calculator app for the given framework."""
    chat = ChatAnthropic(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        max_tokens=4096,
    )

    prompt = PROMPT_TEMPLATE.format(framework=framework)
    response = chat.chat(prompt, echo="none")
    code = strip_markdown_fences(str(response))

    print(f"  Tokens used: {chat.get_tokens()}")
    return code


def main():
    output_root = Path(__file__).parent

    for framework, dirname in FRAMEWORKS.items():
        print(f"\n{'='*60}")
        print(f"Generating app for: {framework}")
        print(f"{'='*60}")

        code = generate_app(framework)

        out_dir = output_root / dirname
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "app.py"
        out_file.write_text(code, encoding="utf-8")

        print(f"  Saved to: {out_file}")

    print(f"\n{'='*60}")
    print("All apps generated successfully!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
