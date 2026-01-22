# llm-framework-showdown

Evaluating Code Quality &amp; Visual Design across Streamlit, Shiny, Dash, Gradio, &amp; Panel

## Gate 1 + Gate 2 runner

This repo includes a small Python runner that:

- Uses `chatlas` (AWS Bedrock Anthropic) to generate an app per (framework × prompt level × model)
- **Gate 1:** runs `py_compile` on the generated `app.py`
- **Gate 2:** starts the app locally and uses Playwright to capture `dashboard.png`
- **Gate 3 (optional):** grades `dashboard.png` via Inspect AI (multimodal)

Outputs are written under `runs/` by default.

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for fast package installation
- AWS credentials configured for Bedrock access (e.g. via `AWS_PROFILE`)
- Playwright browsers installed

### Setup

Install dependencies:

`uv sync`

Install Playwright browsers:

`playwright install`

### Run

Provide the two Bedrock model IDs you want to compare (comma-separated):

`python -m eval_pipeline --models "<MODEL_ID_1>,<MODEL_ID_2>"`

Enable Gate 3 grading (requires an Inspect model string for the grader):

`python -m eval_pipeline --models "<MODEL_ID_1>,<MODEL_ID_2>" --gate3 --gate3-grader-model "anthropic/bedrock/<BEDROCK_MODEL_ID_FOR_SONNET>"`

Common options:

- `--frameworks streamlit,gradio,shiny,panel,dash`
- `--levels beginner,intermediate,advanced,expert`
- `--aws-profile <profile>`
- `--aws-region <region>`
- `--no-gate2` (only compile)
- `--gate3` (run screenshot grading)
- `--gate3-grader-model <model>` (e.g. `anthropic/bedrock/...`)

### Notes

- Gate 2 is implemented for Streamlit, Gradio, Shiny for Python, Panel, and Dash.
