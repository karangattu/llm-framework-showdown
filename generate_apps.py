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

from chatlas import ChatAnthropic, tool_web_search

SYSTEM_PROMPT = (
    "You are an expert Python web developer. "
    "When asked to create an app, your ENTIRE response must be valid Python "
    "source code and nothing else. "
    "Do NOT wrap the code in markdown code fences (no ```). "
    "Do NOT include any commentary, explanation, or prose before or after the code. "
    "Do NOT include any text that is not valid Python. "
    "The very first character of your response must be a Python comment or import. "
    "The very last character must be the end of the Python code. "
    "Do not use any extra packages, CSS, or JavaScript beyond what the specified "
    "web framework already provides out of the box. "
    "If you use web search to look up API details, still respond with ONLY "
    "the Python source code — no search summaries or explanations."
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
    """Extract only valid Python source from LLM output.

    Handles cases where the model wraps code in markdown fences
    or adds prose text before/after the actual Python code.
    """
    # 1. If wrapped in markdown fences, extract the fenced block
    fence_match = re.search(
        r"```(?:python)?\s*\n(.+?)```", code, re.DOTALL
    )
    if fence_match:
        code = fence_match.group(1)

    # 2. Trim any leading non-Python prose (lines before first
    #    import/from/# or common Python keywords)
    lines = code.split("\n")
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and (
            stripped.startswith(("import ", "from ", "#"))
            or stripped.startswith(("def ", "class ", "app"))
        ):
            start = i
            break
    lines = lines[start:]

    # 3. Trim any trailing non-Python text (markdown, prose, etc.)
    #    Walk backwards to find the last line that looks like Python
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if stripped == "":
            continue
        # Lines starting with common markdown/prose indicators
        if stripped.startswith(("MAINTAINABILITY", "READABILITY",
                                "ADHERENCE", "---", "##", "**",
                                "This ", "The ", "Note", "Here")):
            end = i
            continue
        # If it doesn't look like markdown, stop trimming
        break
    lines = lines[:end]

    return "\n".join(lines).strip()


def generate_app(framework: str) -> str:
    """Generate a tip calculator app for the given framework."""
    chat = ChatAnthropic(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        max_tokens=4096,
    )
    chat.register_tool(tool_web_search())

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
