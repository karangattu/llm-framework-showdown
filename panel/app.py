import panel as pn
import param

pn.extension(sizing_mode="stretch_width")

# ── Colour palette ──────────────────────────────────────────────────────────
CLR_HEADER_BG  = "#2C3E50"
CLR_HEADER_FG  = "#FFFFFF"
CLR_CARD_BG    = "#F7F9FC"
CLR_ACCENT     = "#27AE60"
CLR_ACCENT2    = "#2980B9"
CLR_DIVIDER    = "#DDE3EC"
CLR_LABEL      = "#5D6D7E"
CLR_VALUE      = "#1A252F"
CLR_PRESET_ON  = "#27AE60"
CLR_PRESET_OFF = "#ECF0F1"
CLR_PRESET_TXT_ON  = "#FFFFFF"
CLR_PRESET_TXT_OFF = "#2C3E50"

# ── Widgets ──────────────────────────────────────────────────────────────────
bill_input = pn.widgets.FloatInput(
    name="Bill Amount ($)",
    value=50.0,
    step=0.01,
    start=0.0,
    placeholder="Enter bill amount",
    width=260,
)

tip_slider = pn.widgets.FloatSlider(
    name="Custom Tip %",
    value=15.0,
    start=0.0,
    end=100.0,
    step=0.5,
    width=260,
)

preset_15 = pn.widgets.Button(name="15%", button_type="success", width=72)
preset_18 = pn.widgets.Button(name="18%", button_type="default", width=72)
preset_20 = pn.widgets.Button(name="20%", button_type="default", width=72)

split_input = pn.widgets.IntInput(
    name="Split Among (people)",
    value=1,
    start=1,
    end=100,
    step=1,
    width=260,
)

# ── Preset-button callbacks ───────────────────────────────────────────────────
def _update_presets(active_pct):
    """Highlight the active preset button."""
    for btn, pct in [(preset_15, 15), (preset_18, 18), (preset_20, 20)]:
        if abs(active_pct - pct) < 0.01:
            btn.button_type = "success"
        else:
            btn.button_type = "default"

def on_preset_15(event):
    tip_slider.value = 15.0
    _update_presets(15)

def on_preset_18(event):
    tip_slider.value = 18.0
    _update_presets(18)

def on_preset_20(event):
    tip_slider.value = 20.0
    _update_presets(20)

preset_15.on_click(on_preset_15)
preset_18.on_click(on_preset_18)
preset_20.on_click(on_preset_20)

def on_slider_change(event):
    """Deactivate all presets if the slider is moved off a preset value."""
    _update_presets(event.new)

tip_slider.param.watch(on_slider_change, "value")

# ── Result pane ───────────────────────────────────────────────────────────────
def _result_card(bill, tip_pct, people):
    bill    = bill    if bill    is not None else 0.0
    people  = people  if people  is not None else 1
    people  = max(1, people)

    tip_amt    = bill * tip_pct / 100.0
    total      = bill + tip_amt
    per_person = total / people

    def row(label, value, big=False, color=CLR_ACCENT):
        font_size  = "22px" if big else "16px"
        font_weight = "700"  if big else "500"
        return pn.Row(
            pn.pane.Markdown(
                f"<span style='color:{CLR_LABEL};font-size:14px;'>{label}</span>",
                sizing_mode="stretch_width",
            ),
            pn.pane.Markdown(
                f"<span style='color:{color};font-size:{font_size};"
                f"font-weight:{font_weight};'>{value}</span>",
                align="end",
            ),
            sizing_mode="stretch_width",
            margin=(2, 0),
        )

    divider = pn.pane.HTML(
        f"<hr style='border:none;border-top:1px solid {CLR_DIVIDER};"
        "margin:6px 0;'>",
        sizing_mode="stretch_width",
        height=14,
    )

    split_section = []
    if people > 1:
        split_section = [
            divider,
            row(f"Each Person Pays  (÷{people})",
                f"${per_person:,.2f}", big=True, color=CLR_ACCENT2),
        ]

    return pn.Column(
        row("Tip Percentage",  f"{tip_pct:.1f}%"),
        row("Tip Amount",      f"${tip_amt:,.2f}"),
        divider,
        row("Total Bill",      f"${total:,.2f}", big=True),
        *split_section,
        sizing_mode="stretch_width",
        styles={"background": CLR_CARD_BG,
                "border-radius": "10px",
                "padding": "18px 22px",
                "border": f"1px solid {CLR_DIVIDER}"},
    )

result_pane = pn.bind(_result_card, bill_input, tip_slider, split_input)

# ── Layout ────────────────────────────────────────────────────────────────────
header = pn.pane.HTML(
    f"""
    <div style="background:{CLR_HEADER_BG};padding:22px 28px;
                border-radius:12px;margin-bottom:8px;">
      <h1 style="color:{CLR_HEADER_FG};margin:0 0 4px 0;font-size:28px;">
        💰 Tip Calculator
      </h1>
      <p style="color:#B2BFCC;margin:0;font-size:14px;">
        Instantly calculate tip, total, and per-person split.
      </p>
    </div>
    """,
    sizing_mode="stretch_width",
)

section_label = lambda txt: pn.pane.Markdown(
    f"**{txt}**",
    styles={"color": CLR_VALUE, "font-size": "13px", "margin-bottom": "-4px"},
)

input_card = pn.Column(
    section_label("Bill Details"),
    bill_input,
    pn.pane.HTML(
        f"<hr style='border:none;border-top:1px solid {CLR_DIVIDER};"
        "margin:10px 0;'>",
        sizing_mode="stretch_width",
        height=14,
    ),
    section_label("Tip Percentage"),
    pn.Row(preset_15, preset_18, preset_20, margin=(0, 0, 6, 0)),
    tip_slider,
    pn.pane.HTML(
        f"<hr style='border:none;border-top:1px solid {CLR_DIVIDER};"
        "margin:10px 0;'>",
        sizing_mode="stretch_width",
        height=14,
    ),
    section_label("Bill Split"),
    split_input,
    sizing_mode="stretch_width",
    styles={"background": CLR_CARD_BG,
            "border-radius": "10px",
            "padding": "20px 24px",
            "border": f"1px solid {CLR_DIVIDER}"},
)

results_label = pn.pane.Markdown(
    "### 🧾 Results",
    styles={"color": CLR_VALUE},
)

main_layout = pn.Column(
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### ✏️ Inputs", styles={"color": CLR_VALUE}),
            input_card,
            width=340,
        ),
        pn.Spacer(width=24),
        pn.Column(
            results_label,
            result_pane,
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    ),
    sizing_mode="stretch_width",
    max_width=820,
    margin=(20, 0),
)

pn.template.FastListTemplate(
    title="Tip Calculator",
    main=[main_layout],
    theme="default",
    accent="#27AE60",
    header_background=CLR_HEADER_BG,
).servable()