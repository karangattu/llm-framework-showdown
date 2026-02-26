from shiny import App, render, ui, reactive

# ── UI ────────────────────────────────────────────────────────────────────────
app_ui = ui.page_fixed(

    # ── Header ────────────────────────────────────────────────────────────────
    ui.div(
        ui.h1("💰 Tip Calculator", class_="mb-0"),
        ui.p("Enter your bill details below for an instant breakdown.",
             class_="text-muted mt-1"),
        class_="text-center py-4 border-bottom mb-4",
    ),

    # ── Input card ────────────────────────────────────────────────────────────
    ui.card(
        ui.card_header(ui.h5("📋 Bill Details", class_="mb-0")),
        ui.layout_columns(
            # Bill amount
            ui.div(
                ui.input_numeric(
                    "bill",
                    "Bill Amount ($)",
                    value=50.00,
                    min=0,
                    step=0.01,
                ),
            ),
            # Custom tip %
            ui.div(
                ui.input_numeric(
                    "tip_pct",
                    "Tip Percentage (%)",
                    value=18,
                    min=0,
                    max=100,
                    step=1,
                ),
            ),
            col_widths=[6, 6],
        ),

        # ── Preset tip buttons ─────────────────────────────────────────────
        ui.div(
            ui.p("Quick-select tip %:", class_="mb-2 fw-semibold"),
            ui.div(
                ui.input_action_button(
                    "preset_15", "15%",
                    class_="btn btn-outline-secondary me-2",
                ),
                ui.input_action_button(
                    "preset_18", "18%",
                    class_="btn btn-outline-primary me-2",
                ),
                ui.input_action_button(
                    "preset_20", "20%",
                    class_="btn btn-outline-secondary",
                ),
            ),
            class_="mb-2",
        ),
    ),

    ui.br(),

    # ── Results card ──────────────────────────────────────────────────────────
    ui.card(
        ui.card_header(ui.h5("🧾 Your Bill Summary", class_="mb-0")),
        ui.layout_columns(
            # Tip amount
            ui.value_box(
                title="Tip Amount",
                value=ui.output_text("tip_amount"),
                theme="bg-gradient-blue-purple",
            ),
            # Total bill
            ui.value_box(
                title="Total Bill",
                value=ui.output_text("total_bill"),
                theme="bg-gradient-orange-red",
            ),
            col_widths=[6, 6],
        ),
    ),

    ui.br(),

    # ── Split the bill card ───────────────────────────────────────────────────
    ui.card(
        ui.card_header(
            ui.layout_columns(
                ui.h5("👥 Split the Bill", class_="mb-0"),
                ui.div(
                    ui.input_numeric(
                        "num_people",
                        "Number of People",
                        value=2,
                        min=1,
                        step=1,
                    ),
                    class_="",
                ),
                col_widths=[6, 6],
            )
        ),
        ui.layout_columns(
            ui.value_box(
                title="Each Person Pays (tip only)",
                value=ui.output_text("split_tip"),
                theme="bg-gradient-teal-cyan",
            ),
            ui.value_box(
                title="Each Person Pays (total)",
                value=ui.output_text("split_total"),
                theme="bg-gradient-green-teal",
            ),
            col_widths=[6, 6],
        ),
    ),

    ui.br(),

    # ── Footer ────────────────────────────────────────────────────────────────
    ui.div(
        ui.p("Tip amounts are rounded to the nearest cent.", class_="text-muted small"),
        class_="text-center pb-4",
    ),

    title="Tip Calculator",
)


# ── Server ────────────────────────────────────────────────────────────────────
def server(input, output, session):

    # ── Preset button handlers: update tip_pct numeric input ──────────────────
    @reactive.effect
    @reactive.event(input.preset_15)
    def _apply_15():
        ui.update_numeric("tip_pct", value=15)

    @reactive.effect
    @reactive.event(input.preset_18)
    def _apply_18():
        ui.update_numeric("tip_pct", value=18)

    @reactive.effect
    @reactive.event(input.preset_20)
    def _apply_20():
        ui.update_numeric("tip_pct", value=20)

    # ── Reactive calculation ──────────────────────────────────────────────────
    @reactive.calc
    def calc():
        bill = input.bill() or 0.0
        pct  = input.tip_pct() or 0.0
        people = max(int(input.num_people() or 1), 1)

        tip   = round(bill * pct / 100, 2)
        total = round(bill + tip, 2)
        per_person_tip   = round(tip   / people, 2)
        per_person_total = round(total / people, 2)

        return {
            "tip":   tip,
            "total": total,
            "split_tip":   per_person_tip,
            "split_total": per_person_total,
        }

    # ── Outputs ───────────────────────────────────────────────────────────────
    @render.text
    def tip_amount():
        return f"${calc()['tip']:,.2f}"

    @render.text
    def total_bill():
        return f"${calc()['total']:,.2f}"

    @render.text
    def split_tip():
        return f"${calc()['split_tip']:,.2f}"

    @render.text
    def split_total():
        return f"${calc()['split_total']:,.2f}"


# ── App ───────────────────────────────────────────────────────────────────────
app = App(app_ui, server)