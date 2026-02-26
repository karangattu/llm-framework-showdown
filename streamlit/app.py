import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tip Calculator",
    page_icon="💰",
    layout="centered",
)

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("💰 Tip Calculator")
st.markdown("Calculate your tip and total bill instantly.")
st.divider()

# ── Bill Amount ───────────────────────────────────────────────────────────────
st.subheader("🧾 Bill Details")

bill_amount = st.number_input(
    label="Bill Amount ($)",
    min_value=0.0,
    value=0.0,
    step=0.01,
    format="%.2f",
    placeholder="Enter the total bill amount...",
    help="Enter the pre-tip bill amount in dollars.",
)

st.markdown("**Select a Tip Percentage**")

# ── Tip Preset Buttons ────────────────────────────────────────────────────────
# Use session state to track selected preset vs custom slider value
if "tip_pct" not in st.session_state:
    st.session_state["tip_pct"] = 18

col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    if st.button("15%  —  Standard", use_container_width=True):
        st.session_state["tip_pct"] = 15
with col_p2:
    if st.button("18%  —  Good", use_container_width=True):
        st.session_state["tip_pct"] = 18
with col_p3:
    if st.button("20%  —  Great", use_container_width=True):
        st.session_state["tip_pct"] = 20

# ── Custom Tip Slider ─────────────────────────────────────────────────────────
tip_pct = st.slider(
    label="Or choose a custom tip percentage",
    min_value=0,
    max_value=50,
    value=st.session_state["tip_pct"],
    step=1,
    format="%d%%",
    help="Drag to set a custom tip percentage (0 – 50%).",
)

# Keep session state in sync with the slider when user drags it manually
st.session_state["tip_pct"] = tip_pct

st.divider()

# ── Calculations ──────────────────────────────────────────────────────────────
tip_amount  = bill_amount * tip_pct / 100
total_bill  = bill_amount + tip_amount

# ── Results ───────────────────────────────────────────────────────────────────
st.subheader("📊 Results")

res_col1, res_col2, res_col3 = st.columns(3)

res_col1.metric(
    label="Tip Percentage",
    value=f"{tip_pct}%",
)
res_col2.metric(
    label="Tip Amount",
    value=f"${tip_amount:,.2f}",
)
res_col3.metric(
    label="Total Bill",
    value=f"${total_bill:,.2f}",
)

st.divider()

# ── Bill Splitter (Optional Feature) ─────────────────────────────────────────
st.subheader("🍽️ Split the Bill")

split_on = st.toggle("Split the total among multiple people", value=False)

if split_on:
    num_people = st.number_input(
        label="Number of People",
        min_value=2,
        max_value=100,
        value=2,
        step=1,
        help="How many people are sharing the bill?",
    )

    if num_people >= 2:
        per_person_total = total_bill / num_people
        per_person_tip   = tip_amount / num_people

        st.markdown(f"Splitting **\${total_bill:,.2f}** among **{int(num_people)} people**:")

        sp_col1, sp_col2 = st.columns(2)
        sp_col1.metric(
            label="Each Person Pays (Tip)",
            value=f"${per_person_tip:,.2f}",
        )
        sp_col2.metric(
            label="Each Person Pays (Total)",
            value=f"${per_person_total:,.2f}",
        )

st.divider()

# ── Summary caption ───────────────────────────────────────────────────────────
if bill_amount > 0:
    st.caption(
        f"📌 A {tip_pct}% tip on a **\${bill_amount:,.2f}** bill "
        f"is **\${tip_amount:,.2f}**, making your total **\${total_bill:,.2f}**."
        + (
            f" Split {int(num_people)} ways, each person owes **\${per_person_total:,.2f}**."
            if split_on and num_people >= 2
            else ""
        )
    )
else:
    st.caption("👆 Enter a bill amount above to see your results instantly.")
