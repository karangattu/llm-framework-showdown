import dash
from dash import dcc, html, Input, Output, State

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Tip Calculator", style={"textAlign": "center", "marginBottom": "30px", "color": "#2c3e50"}),

    html.Div([
        # Bill Amount Input
        html.Div([
            html.Label("Bill Amount ($)", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
            dcc.Input(
                id="bill-amount",
                type="number",
                placeholder="Enter bill amount",
                min=0,
                step=0.01,
                style={"width": "100%", "padding": "10px", "fontSize": "16px", "borderRadius": "5px", "border": "1px solid #ccc", "boxSizing": "border-box"}
            ),
        ], style={"marginBottom": "20px"}),

        # Tip Percentage
        html.Div([
            html.Label("Tip Percentage (%)", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
            html.Div([
                html.Button("15%", id="btn-15", n_clicks=0, style={"marginRight": "8px", "padding": "8px 16px", "borderRadius": "5px", "border": "1px solid #3498db", "backgroundColor": "#3498db", "color": "white", "cursor": "pointer", "fontSize": "14px"}),
                html.Button("18%", id="btn-18", n_clicks=0, style={"marginRight": "8px", "padding": "8px 16px", "borderRadius": "5px", "border": "1px solid #3498db", "backgroundColor": "white", "color": "#3498db", "cursor": "pointer", "fontSize": "14px"}),
                html.Button("20%", id="btn-20", n_clicks=0, style={"marginRight": "8px", "padding": "8px 16px", "borderRadius": "5px", "border": "1px solid #3498db", "backgroundColor": "white", "color": "#3498db", "cursor": "pointer", "fontSize": "14px"}),
            ], style={"marginBottom": "8px"}),
            dcc.Input(
                id="tip-percent",
                type="number",
                placeholder="Or enter custom %",
                min=0,
                max=100,
                step=0.5,
                style={"width": "100%", "padding": "10px", "fontSize": "16px", "borderRadius": "5px", "border": "1px solid #ccc", "boxSizing": "border-box"}
            ),
        ], style={"marginBottom": "20px"}),

        # Number of People
        html.Div([
            html.Label("Split Among (people)", style={"fontWeight": "bold", "marginBottom": "5px", "display": "block"}),
            dcc.Input(
                id="num-people",
                type="number",
                value=1,
                min=1,
                step=1,
                style={"width": "100%", "padding": "10px", "fontSize": "16px", "borderRadius": "5px", "border": "1px solid #ccc", "boxSizing": "border-box"}
            ),
        ], style={"marginBottom": "30px"}),

        # Results
        html.Div([
            html.H3("Results", style={"color": "#2c3e50", "marginBottom": "15px", "borderBottom": "2px solid #3498db", "paddingBottom": "8px"}),
            html.Div([
                html.Div([
                    html.Span("Tip Amount:", style={"fontWeight": "bold", "color": "#555"}),
                    html.Span(id="tip-amount", style={"float": "right", "fontWeight": "bold", "color": "#27ae60", "fontSize": "18px"}),
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "12px 0", "borderBottom": "1px solid #eee"}),

                html.Div([
                    html.Span("Total Bill:", style={"fontWeight": "bold", "color": "#555"}),
                    html.Span(id="total-bill", style={"float": "right", "fontWeight": "bold", "color": "#2980b9", "fontSize": "18px"}),
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "12px 0", "borderBottom": "1px solid #eee"}),

                html.Div([
                    html.Span("Per Person:", style={"fontWeight": "bold", "color": "#555"}),
                    html.Span(id="per-person", style={"float": "right", "fontWeight": "bold", "color": "#8e44ad", "fontSize": "18px"}),
                ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "padding": "12px 0"}),
            ], style={"backgroundColor": "#f9f9f9", "padding": "15px", "borderRadius": "8px"}),
        ]),

        html.Div(id="error-msg", style={"color": "red", "marginTop": "15px", "textAlign": "center"}),

    ], style={
        "maxWidth": "480px",
        "margin": "0 auto",
        "backgroundColor": "white",
        "padding": "30px",
        "borderRadius": "10px",
        "boxShadow": "0 4px 20px rgba(0,0,0,0.1)"
    }),

], style={"backgroundColor": "#ecf0f1", "minHeight": "100vh", "padding": "40px 20px", "fontFamily": "Arial, sans-serif"})


@app.callback(
    Output("tip-percent", "value"),
    Input("btn-15", "n_clicks"),
    Input("btn-18", "n_clicks"),
    Input("btn-20", "n_clicks"),
    prevent_initial_call=True
)
def set_preset_tip(n15, n18, n20):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "btn-15":
        return 15
    elif button_id == "btn-18":
        return 18
    elif button_id == "btn-20":
        return 20
    return dash.no_update


@app.callback(
    Output("tip-amount", "children"),
    Output("total-bill", "children"),
    Output("per-person", "children"),
    Output("error-msg", "children"),
    Input("bill-amount", "value"),
    Input("tip-percent", "value"),
    Input("num-people", "value"),
)
def calculate(bill, tip_pct, num_people):
    if bill is None and tip_pct is None:
        return "—", "—", "—", ""

    if bill is None or bill < 0:
        return "—", "—", "—", "Please enter a valid bill amount."

    if tip_pct is None or tip_pct < 0 or tip_pct > 100:
        return "—", "—", "—", "Please enter a valid tip percentage (0–100)."

    people = num_people if num_people and num_people >= 1 else 1

    tip = bill * (tip_pct / 100)
    total = bill + tip
    per_person = total / people

    return f"${tip:.2f}", f"${total:.2f}", f"${per_person:.2f}", ""


if __name__ == "__main__":
    app.run(debug=True)