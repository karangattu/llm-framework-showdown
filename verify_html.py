import re
from pathlib import Path

html = Path("index.html").read_text()

sections = {
    "Streamlit": r"Streamlit – Evaluation(.+?)Plotly Dash – Evaluation",
    "Dash": r"Plotly Dash – Evaluation(.+?)Panel – Evaluation",
    "Panel": r"Panel – Evaluation(.+?)Shiny for Python – Evaluation",
    "Shiny": r"Shiny for Python – Evaluation(.+?)$",
}

for name, pattern in sections.items():
    m = re.search(pattern, html, re.DOTALL)
    if m:
        sec = m.group(1)
        uls = len(re.findall(r"<ul>", sec))
        lis = len(re.findall(r"<li>", sec))
        print(f"{name:12s}: {uls} <ul>, {lis} <li>")
