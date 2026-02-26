# Tip Calculator — Plotly Dash App

from dash import Dash, dcc, html, Input, Output, callback

# ---------------------------------------------------------------------------
# App instance
# ---------------------------------------------------------------------------
app = Dash(__name__)
app.title = "Tip Calculator"

# ---------------------------------------------------------------------------
# Reusable style constants  (plain Python dicts – no external CSS/JS)
# ---------------------------------------------------------------------------
PAGE_BG      = "#f0f4f8"
CARD_BG      = "#ffffff"
PRIMARY      = "#4f8ef7"
PRIMARY_DARK = "#3a6fd8"
SUCCESS_BG   = "#eaf4ea"
SUCCESS_FG   = "#2d7a2d"
BORDER       = "#dde3ec"
LABEL_COLOR  = "#4a5568"
MUTED        = "#718096"
HEADING      = "#1a202c"

page_style = {
    "minHeight": "100vh",
    "backgroundColor": PAGE_BG,
    "fontFamily": "'Segoe UI', Arial, sans-serif",
    "display": "flex",
    "alignItems": "flex-start",
    "justifyContent": "center",
    "padding": "40px 16px",
    "boxSizing": "border-box",
}

card_style = {
    "backgroundColor": CARD_BG,
    "borderRadius": "16px",
    "boxShadow": "0 4px 24px rgba(0,0,0,0.10)",
    "padding": "36px 40px 32px 40px",
    "width": "100%",
    "maxWidth": "480px",
    "boxSizing": "border-box",
}

section_style = {
    "backgroundColor": "#f7f9fc",
    "border": f"1px solid {BORDER}",
    "borderRadius": "10px",
    "padding": "20px 20px 16px 20px",
    "marginBottom": "22px",
}

label_style = {
    "display": "block",
    "fontSize": "13px",
    "fontWeight": "600",
    "color": LABEL_COLOR,
    "marginBottom": "7px",
    "letterSpacing": "0.03em",
    "textTransform": "uppercase",
}

input_style = {
    "width": "100%",
    "padding": "10px 14px",
    "fontSize": "16px",
    "borderRadius": "8px",
    "border": f"1.5px solid {BORDER}",
    "outline": "none",
    "backgroundColor": "#fff",
    "color": HEADING,
    "boxSizing": "border-box",
}

preset_btn_base = {
    "padding": "8px 0",
    "width": "30%",
    "fontSize": "14px",
    "fontWeight": "600",
    "border": f"1.5px solid {PRIMARY}",
    "borderRadius": "7px",
    "cursor": "pointer",
    "transition": "all 0.15s",
}

preset_btn_active = {**preset_btn_base,
                     "backgroundColor": PRIMARY,
                     "color": "#fff"}

preset_btn_inactive = {**preset_btn_base,
                       "backgroundColor": "#fff",
                       "color": PRIMARY}

result_card_style = {
    "backgroundColor": SUCCESS_BG,
    "border": f"1px solid #b7dfb7",
    "borderRadius": "10px",
    "padding": "20px 24px",
    "marginBottom": "22px",
}

result_row_style = {
    "display": "flex",
    "justifyContent": "space-between",
    "alignItems": "center",
    "padding": "6px 0",
}

result_label_style = {
    "fontSize": "14px",
    "color": SUCCESS_FG,
    "fontWeight": "500",
}

result_value_style = {
    "fontSize": "18px",
    "fontWeight": "700",
    "color": SUCCESS_FG,
}

total_label_style = {
    **result_label_style,
    "fontSize": "16px",
    "fontWeight": "700",
}

total_value_style = {
    **result_value_style,
    "fontSize": "24px",
}

divider_style = {
    "border": "none",
    "borderTop": f"1px solid #b7dfb7",
    "margin": "10px 0",
}

split_card_style = {
    "backgroundColor": "#f0f4ff",
    "border": f"1px solid #c5d3f5",
    "borderRadius": "10px",
    "padding": "20px 24px",
    "marginBottom": "8px",
}

split_value_style = {
    "fontSize": "22px",
    "fontWeight": "700",
    "color": PRIMARY_DARK,
    "textAlign": "center",
    "margin": "6px 0 0 0",
}

split_label_main = {
    "fontSize": "13px",
    "fontWeight": "600",
    "color": "#3a5a9e",
    "textTransform": "uppercase",
    "letterSpacing": "0.04em",
    "textAlign": "center",
    "margin": "0",
}

error_style = {
    "color": "#c0392b",
    "fontSize": "13px",
    "marginTop": "6px",
    "minHeight": "18px",
}

footer_style = {
    "textAlign": "center",
    "color": MUTED,
    "fontSize": "12px",
    "marginTop": "10px",
}

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
app.layout = html.Div(style=page_style, children=[
    html.Div(style=card_style, children=[

        # ── Header ──────────────────────────────────────────────────────────
        html.Div(style={"textAlign": "center", "marginBottom": "28px"}, children=[
            html.Div("💰", style={"fontSize": "40px", "lineHeight": "1", "marginBottom": "8px"}),
            html.H1("Tip Calculator",
                    style={"margin": "0 0 4px 0", "fontSize": "26px",
                           "fontWeight": "700", "color": HEADING}),
            html.P("Fast, clean and fair tip splitting.",
                   style={"margin": "0", "color": MUTED, "fontSize": "14px"}),
        ]),

        # ── Bill Amount ──────────────────────────────────────────────────────
        html.Div(style=section_style, children=[
            html.Label("Bill Amount ($)", style=label_style),
            dcc.Input(
                id="bill-amount",
                type="number",
                placeholder="e.g. 85.50",
                min=0,
                step=0.01,
                debounce=False,
                style=input_style,
            ),
            html.Div(id="bill-error", style=error_style),
        ]),

        # ── Tip Percentage ───────────────────────────────────────────────────
        html.Div(style=section_style, children=[
            html.Label("Tip Percentage (%)", style=label_style),

            # Preset buttons row
            html.Div(
                style={"display": "flex", "justifyContent": "space-between",
                       "gap": "8px", "marginBottom": "14px"},
                children=[
                    html.Button("15%", id="btn-15", n_clicks=0,
                                style=preset_btn_inactive),
                    html.Button("18%", id="btn-18", n_clicks=0,
                                style=preset_btn_inactive),
                    html.Button("20%", id="btn-20", n_clicks=0,
                                style=preset_btn_inactive),
                ]
            ),

            # Custom tip input
            html.Label("Or enter a custom tip %", style={
                **label_style, "textTransform": "none", "fontSize": "12px",
                "color": MUTED, "marginBottom": "6px",
            }),
            dcc.Input(
                id="tip-percent",
                type="number",
                placeholder="e.g. 22",
                min=0,
                max=100,
                step=0.5,
                debounce=False,
                style=input_style,
            ),
            html.Div(id="tip-error", style=error_style),
        ]),

        # ── Results ──────────────────────────────────────────────────────────
        html.Div(id="results-section", style=result_card_style, children=[
            html.Div(style=result_row_style, children=[
                html.Span("Tip Amount", style=result_label_style),
                html.Span(id="tip-amount", style=result_value_style),
            ]),
            html.Hr(style=divider_style),
            html.Div(style=result_row_style, children=[
                html.Span("Total Bill", style=total_label_style),
                html.Span(id="total-amount", style=total_value_style),
            ]),
        ]),

        # ── Bill Split ───────────────────────────────────────────────────────
        html.Div(style=section_style, children=[
            html.Label("Split Among (people)", style=label_style),
            dcc.Input(
                id="num-people",
                type="number",
                placeholder="e.g. 4",
                min=1,
                max=100,
                step=1,
                value=1,
                debounce=False,
                style=input_style,
            ),
            html.Div(id="split-error", style=error_style),
        ]),

        html.Div(id="split-section", style=split_card_style, children=[
            html.P("Each Person Pays", style=split_label_main),
            html.P(id="per-person", style=split_value_style),
        ]),

        # ── Footer ───────────────────────────────────────────────────────────
        html.P("Tip = Bill × Tip %   |   Total = Bill + Tip",
               style=footer_style),
    ])
])


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

# 1. Sync preset buttons → tip-percent input & highlight active button
@callback(
    Output("tip-percent",  "value"),
    Output("btn-15",       "style"),
    Output("btn-18",       "style"),
    Output("btn-20",       "style"),
    Input("btn-15",        "n_clicks"),
    Input("btn-18",        "n_clicks"),
    Input("btn-20",        "n_clicks"),
    Input("tip-percent",   "value"),
)
def sync_preset(n15, n18, n20, custom_val):
    from dash import ctx

    triggered = ctx.triggered_id

    # Map button ids to tip values
    preset_map = {"btn-15": 15, "btn-18": 18, "btn-20": 20}

    if triggered in preset_map:
        chosen_val = preset_map[triggered]
    else:
        # User typed a custom value; keep it, no preset active
        chosen_val = custom_val

    def btn_style(tip_val):
        if chosen_val == tip_val and triggered in preset_map:
            return preset_btn_active
        return preset_btn_inactive

    return chosen_val, btn_style(15), btn_style(18), btn_style(20)


# 2. Calculate tip, total, per-person
@callback(
    Output("tip-amount",    "children"),
    Output("total-amount",  "children"),
    Output("per-person",    "children"),
    Output("bill-error",    "children"),
    Output("tip-error",     "children"),
    Output("split-error",   "children"),
    Input("bill-amount",    "value"),
    Input("tip-percent",    "value"),
    Input("num-people",     "value"),
)
def calculate(bill, tip_pct, num_people):
    bill_err  = ""
    tip_err   = ""
    split_err = ""

    # Validate bill
    if bill is None:
        return "—", "—", "—", bill_err, tip_err, split_err
    if bill < 0:
        bill_err = "⚠ Bill amount cannot be negative."
        return "—", "—", "—", bill_err, tip_err, split_err

    # Validate tip
    if tip_pct is None:
        return "—", "—", "—", bill_err, "⚠ Please select or enter a tip %.", split_err
    if tip_pct < 0 or tip_pct > 100:
        tip_err = "⚠ Tip % must be between 0 and 100."
        return "—", "—", "—", bill_err, tip_err, split_err

    tip_amount  = bill * (tip_pct / 100)
    total       = bill + tip_amount

    # Validate split
    if num_people is None or num_people < 1:
        split_err = "⚠ Number of people must be at least 1."
        per_person_str = "—"
    else:
        per_person = total / int(num_people)
        per_person_str = f"${per_person:,.2f}"

    return (
        f"${tip_amount:,.2f}",
        f"${total:,.2f}",
        per_person_str,
        bill_err,
        tip_err,
        split_err,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)