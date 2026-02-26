I'll analyze the app code and screenshots across the three criteria.

#### Criterion 1: Maintainability (Score: 8/10)

**Strengths:**

- Code is well-organized with clear section comments using visual separators (`# ──`)
- Logical flow: config → inputs → calculations → outputs → split feature
- Session state is used appropriately for the tip percentage persistence
- Calculations are isolated into simple, clear formulas
- Good use of columns for layout consistency

**Weaknesses:**

- The summary caption at the bottom references `num_people` which could cause a `NameError` if `split_on` is True but the variable is somehow not defined (minor scoping risk)
- No functions/helpers — everything is inline, which makes future refactoring slightly harder
- The "Splitting ... among **2 people**" bug (visible in after screenshot) indicates a display logic issue

#### Criterion 2: Readability (Score: 9/10)

**Strengths:**

- Excellent inline comments with clear section headers
- Descriptive variable names (`bill_amount`, `tip_pct`, `per_person_total`, etc.)
- Follows idiomatic Streamlit patterns (session state, columns, metrics)
- Help text on inputs adds to self-documentation
- Logical top-to-bottom flow mirrors the UI layout

**Weaknesses:**

- Minor: the session state sync pattern (setting after slider) is slightly confusing since the buttons set it before and the slider reads it — understandable but not immediately obvious

#### Criterion 3: Requirement Adherence (Score: 8/10)

**Strengths:**

- ✅ Input field for bill amount
- ✅ 15%, 18%, 20% preset buttons are present
- ✅ Custom tip slider also available
- ✅ Instant calculation of tip amount and total bill displayed
- ✅ Bill splitting feature implemented
- ✅ No extra packages, CSS, or JavaScript used
- ✅ Before screenshot confirms clean default state

**Weaknesses:**

- ❌ **Bug confirmed in after screenshot**: "Splitting $102.60 among **2 people**" is shown even though 3 people are entered (the number input shows 3 but the text says 2 — likely a Streamlit re-run/state timing issue where `num_people` lags one interaction)
- The split toggle adds a small UX friction — could default to showing the split section more prominently
- The "20% — Great" button in the after screenshot appears slightly highlighted but there's no clear visual indicator of the selected preset
