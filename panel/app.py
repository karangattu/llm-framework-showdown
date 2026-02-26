import panel as pn

pn.extension()

# Widgets
bill_input = pn.widgets.NumberInput(
    name="Bill Amount ($)",
    value=0.0,
    step=0.01,
    start=0.0,
    placeholder="Enter bill amount",
    width=300,
)

tip_preset = pn.widgets.RadioButtonGroup(
    name="Tip Preset",
    options=["15%", "18%", "20%", "Custom"],
    value="15%",
    button_type="primary",
    width=300,
)

tip_custom = pn.widgets.NumberInput(
    name="Custom Tip (%)",
    value=15.0,
    step=0.5,
    start=0.0,
    end=100.0,
    width=300,
    disabled=True,
)

num_people = pn.widgets.IntSlider(
    name="Split Among (people)",
    value=1,
    start=1,
    end=20,
    step=1,
    width=300,
)

# Result displays
tip_amount_display = pn.widgets.StaticText(name="Tip Amount", value="$0.00")
total_display = pn.widgets.StaticText(name="Total Bill", value="$0.00")
per_person_display = pn.widgets.StaticText(name="Per Person", value="$0.00")

def update_custom_tip(event):
    if event.new == "Custom":
        tip_custom.disabled = False
    else:
        tip_custom.disabled = True
        preset_map = {"15%": 15.0, "18%": 18.0, "20%": 20.0}
        tip_custom.value = preset_map.get(event.new, 15.0)

tip_preset.param.watch(update_custom_tip, "value")

def calculate(event=None):
    bill = bill_input.value if bill_input.value is not None else 0.0
    tip_pct = tip_custom.value if tip_custom.value is not None else 0.0
    people = num_people.value if num_people.value and num_people.value > 0 else 1

    tip_amt = bill * (tip_pct / 100.0)
    total = bill + tip_amt
    per_person = total / people

    tip_amount_display.value = f"${tip_amt:.2f}"
    total_display.value = f"${total:.2f}"

    if people > 1:
        per_person_display.name = f"Per Person ({people} people)"
        per_person_display.value = f"${per_person:.2f}"
    else:
        per_person_display.name = "Per Person"
        per_person_display.value = f"${per_person:.2f}"

bill_input.param.watch(calculate, "value")
tip_custom.param.watch(calculate, "value")
num_people.param.watch(calculate, "value")

calculate()

divider = pn.layout.Divider()

layout = pn.Column(
    pn.pane.Markdown("# 🧾 Tip Calculator"),
    pn.layout.Divider(),
    pn.pane.Markdown("### Enter Bill Details"),
    bill_input,
    pn.pane.Markdown("### Select Tip Percentage"),
    tip_preset,
    tip_custom,
    pn.layout.Divider(),
    pn.pane.Markdown("### Results"),
    tip_amount_display,
    total_display,
    pn.layout.Divider(),
    pn.pane.Markdown("### Split the Bill"),
    num_people,
    per_person_display,
    width=400,
    margin=(20, 20),
)

layout.servable()