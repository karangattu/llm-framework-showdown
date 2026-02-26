from shiny import App, ui, render, reactive

app_ui = ui.page_fluid(
    ui.h2("Tip Calculator", style="text-align: center; margin-bottom: 20px;"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Bill Details"),
            ui.input_numeric(
                "bill_amount",
                "Bill Amount ($)",
                value=50.00,
                min=0,
                step=0.01,
            ),
            ui.input_radio_buttons(
                "tip_preset",
                "Tip Percentage Presets",
                choices={"15": "15%", "18": "18%", "20": "20%", "custom": "Custom"},
                selected="18",
                inline=True,
            ),
            ui.panel_conditional(
                "input.tip_preset === 'custom'",
                ui.input_numeric(
                    "custom_tip",
                    "Custom Tip (%)",
                    value=18,
                    min=0,
                    max=100,
                    step=1,
                ),
            ),
            ui.input_numeric(
                "num_people",
                "Number of People (to split the bill)",
                value=1,
                min=1,
                step=1,
            ),
        ),
        ui.card(
            ui.card_header("Calculation Results"),
            ui.output_ui("results"),
        ),
        col_widths=[6, 6],
    ),
)


def server(input, output, session):
    @reactive.calc
    def tip_percentage():
        if input.tip_preset() == "custom":
            val = input.custom_tip()
            if val is None or val < 0:
                return 0
            return val
        else:
            return float(input.tip_preset())

    @reactive.calc
    def calculations():
        bill = input.bill_amount()
        if bill is None or bill < 0:
            bill = 0

        tip_pct = tip_percentage()
        num_people = input.num_people()
        if num_people is None or num_people < 1:
            num_people = 1

        tip_amount = bill * (tip_pct / 100)
        total = bill + tip_amount
        per_person = total / num_people
        tip_per_person = tip_amount / num_people

        return {
            "bill": bill,
            "tip_pct": tip_pct,
            "tip_amount": tip_amount,
            "total": total,
            "num_people": num_people,
            "per_person": per_person,
            "tip_per_person": tip_per_person,
        }

    @output
    @render.ui
    def results():
        c = calculations()

        rows = [
            ("Bill Amount", f"${c['bill']:.2f}"),
            ("Tip Percentage", f"{c['tip_pct']:.1f}%"),
            ("Tip Amount", f"${c['tip_amount']:.2f}"),
            ("Total Bill", f"${c['total']:.2f}"),
        ]

        table_rows = []
        for label, value in rows:
            table_rows.append(
                ui.tags.tr(
                    ui.tags.td(
                        ui.tags.strong(label),
                        style="padding: 8px 12px; border-bottom: 1px solid #dee2e6;",
                    ),
                    ui.tags.td(
                        value,
                        style="padding: 8px 12px; border-bottom: 1px solid #dee2e6; text-align: right;",
                    ),
                )
            )

        if c["num_people"] > 1:
            split_rows = [
                ("Number of People", str(int(c["num_people"]))),
                ("Tip Per Person", f"${c['tip_per_person']:.2f}"),
                ("Total Per Person", f"${c['per_person']:.2f}"),
            ]
            table_rows.append(
                ui.tags.tr(
                    ui.tags.td(
                        ui.tags.em("— Split Details —"),
                        colspan="2",
                        style="padding: 8px 12px; background-color: #f8f9fa; text-align: center; border-bottom: 1px solid #dee2e6;",
                    )
                )
            )
            for label, value in split_rows:
                table_rows.append(
                    ui.tags.tr(
                        ui.tags.td(
                            ui.tags.strong(label),
                            style="padding: 8px 12px; border-bottom: 1px solid #dee2e6;",
                        ),
                        ui.tags.td(
                            value,
                            style="padding: 8px 12px; border-bottom: 1px solid #dee2e6; text-align: right;",
                        ),
                    )
                )

        return ui.tags.table(
            ui.tags.tbody(*table_rows),
            style="width: 100%; border-collapse: collapse; font-size: 1rem;",
        )


app = App(app_ui, server)