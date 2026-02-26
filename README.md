# LLM Framework Showdown

Generate a basic **tip calculator** web app for four Python web frameworks using an LLM — then compare the results side-by-side.

The generator script uses [chatlas](https://posit-dev.github.io/chatlas/) with Anthropic's `claude-sonnet-4-6` to produce a self-contained `app.py` for each framework:

| Framework | Directory | Run command |
|---|---|---|
| Streamlit | `streamlit/` | `streamlit run streamlit/app.py` |
| Plotly Dash | `dash/` | `python dash/app.py` |
| Panel | `panel/` | `panel serve panel/app.py` |
| Shiny for Python | `shiny/` | `shiny run shiny/app.py` |

## Prerequisites

- Python 3.13+
- `ANTHROPIC_API_KEY` environment variable set

## Setup

```bash
pip install -r requirements.txt
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install -r requirements.txt
```

## Generate the apps

```bash
python generate_apps.py
```

This calls `claude-sonnet-4-6` once per framework and saves each generated app to its own directory.

## Run a generated app

```bash
# Streamlit
streamlit run streamlit/app.py

# Plotly Dash
python dash/app.py

# Panel
panel serve panel/app.py

# Shiny for Python
shiny run shiny/app.py
```
