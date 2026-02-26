I'll evaluate this Plotly Dash tip calculator app across the three criteria.

---

#### Criterion 1: Maintainability

**Strengths:**

- Style constants are centralized at the top using named color variables (`PRIMARY`, `CARD_BG`, etc.), making global theme changes easy
- The two callbacks are well-separated by concern (one for syncing presets, one for calculations)
- The layout is logically organized into clearly named sections (Bill Amount, Tip Percentage, Results, Split)
- Style dictionaries use composition (`{**preset_btn_base, ...}`) to reduce duplication
- Good use of constants to avoid magic numbers/strings

**Weaknesses:**

- The large number of style dictionaries (15+) at the module level creates a long file that's somewhat monolithic — a larger project would benefit from separating styles
- The `sync_preset` callback imports `ctx` inside the function rather than at module level
- Some mild logic duplication in the `btn_style` inner function

**Score: 8/10**

---

#### Criterion 2: Readability

**Strengths:**

- Excellent use of section comments (`# ── Bill Amount ──...`) that visually separate layout blocks
- Variable names are descriptive and self-documenting (`bill_err`, `tip_amount`, `per_person_str`)
- The `preset_map` dictionary elegantly maps button IDs to values
- The file-level comment "Tip Calculator — Plotly Dash App" and section headers guide readers well
- Callback logic is clean and follows a clear validate-then-compute pattern

**Weaknesses:**

- The density of style dictionaries near the top is visually overwhelming and may slow down reading the actual app logic
- Minor: `from dash import ctx` inside the callback is unconventional and could confuse readers expecting all imports at the top

**Score: 8/10**

---

#### Criterion 3: Requirement Adherence

**Strengths:**

- ✅ Input field for bill amount with proper number input
- ✅ Input field for tip percentage (custom)
- ✅ All three preset buttons (15%, 18%, 20%) present and functional
- ✅ Active preset button highlights correctly (20% shown filled/blue in "after" screenshot)
- ✅ Instant calculation — tip amount ($17.10) and total bill ($102.60) shown correctly for $85.50 @ 20%
- ✅ Split among multiple people works correctly ($102.60 ÷ 3 = $34.20 confirmed in screenshot)
- ✅ No external CSS files, JS files, or extra packages used — only Dash's built-in inline styles
- ✅ Input validation with error messages for edge cases
- ✅ Clean, professional interface

**Weaknesses:**

- Essentially none — all requirements are fully met and verified by screenshots

**Score: 10/10**

---
