import streamlit as st

st.title("💰 Tip Calculator")
st.write("Calculate your tip quickly and easily.")

st.subheader("Bill Details")

bill_amount = st.number_input(
    "Bill Amount ($)",
    min_value=0.0,
    value=0.0,
    step=0.01,
    format="%.2f"
)

st.subheader("Tip Percentage")

preset_col1, preset_col2, preset_col3 = st.columns(3)

with preset_col1:
    btn_15 = st.button("15%", use_container_width=True)
with preset_col2:
    btn_18 = st.button("18%", use_container_width=True)
with preset_col3:
    btn_20 = st.button("20%", use_container_width=True)

if "tip_pct" not in st.session_state:
    st.session_state["tip_pct"] = 15.0

if btn_15:
    st.session_state["tip_pct"] = 15.0
elif btn_18:
    st.session_state["tip_pct"] = 18.0
elif btn_20:
    st.session_state["tip_pct"] = 20.0

tip_percentage = st.slider(
    "Or choose a custom tip percentage:",
    min_value=0,
    max_value=50,
    value=int(st.session_state["tip_pct"]),
    step=1,
    format="%d%%"
)

st.session_state["tip_pct"] = float(tip_percentage)

st.subheader("Split the Bill (Optional)")

num_people = st.number_input(
    "Number of People",
    min_value=1,
    value=1,
    step=1
)

tip_amount = bill_amount * (tip_percentage / 100)
total_bill = bill_amount + tip_amount

st.subheader("Results")

if bill_amount > 0:
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Tip Amount", f"${tip_amount:.2f}")

    with col2:
        st.metric("Total Bill", f"${total_bill:.2f}")

    if num_people > 1:
        st.write("---")
        st.subheader(f"Split Among {num_people} People")

        tip_per_person = tip_amount / num_people
        total_per_person = total_bill / num_people
        bill_per_person = bill_amount / num_people

        col3, col4, col5 = st.columns(3)

        with col3:
            st.metric("Bill per Person", f"${bill_per_person:.2f}")

        with col4:
            st.metric("Tip per Person", f"${tip_per_person:.2f}")

        with col5:
            st.metric("Total per Person", f"${total_per_person:.2f}")

    st.write("---")
    st.write("**Summary**")
    summary_data = {
        "Item": ["Bill Amount", f"Tip ({tip_percentage}%)", "Total Bill"],
        "Amount": [f"${bill_amount:.2f}", f"${tip_amount:.2f}", f"${total_bill:.2f}"]
    }
    st.table(summary_data)

else:
    st.info("Enter a bill amount above to see your tip calculation.")