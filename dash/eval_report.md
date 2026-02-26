I'll evaluate this Plotly Dash tip calculator app on three criteria.

#### Criterion 1: Maintainability (Score: 7/10)

**Strengths:**

- Clear separation between layout and callback logic
- Two focused callbacks with single responsibilities
- Meaningful component IDs (`bill-amount`, `tip-percent`, `num-people`, `btn-15`, etc.)
- Good input validation logic in the calculation callback

**Weaknesses:**

- Inline styles are heavily repeated throughout, making style updates tedious (e.g., the button styles are copy-pasted with minor variations)
- Style dictionaries could be extracted into named constants at the top of the file
- The button highlighting logic has a bug: the "15%" button always appears highlighted (blue fill) regardless of which preset was last clicked, since button styles are static in the layout
- A shared style dictionary for common patterns would improve maintainability significantly

#### Criterion 2: Readability (Score: 7/10)

**Strengths:**

- Code is logically organized: layout first, then callbacks
- Variable names are descriptive (`bill`, `tip_pct`, `num_people`, `per_person`)
- Callback logic is straightforward and easy to follow
- Comments (e.g., `# Bill Amount Input`, `# Tip Percentage`, `# Results`) help navigate the layout

**Weaknesses:**

- The massive inline style dictionaries make the layout section visually noisy and hard to scan
- No docstrings or module-level comments explaining the app's purpose
- The `prevent_initial_call=True` usage is idiomatic, but the `ctx.triggered` check is slightly redundant given that flag
- Could use `dash.ctx` (modern API) instead of `dash.callback_context`

#### Criterion 3: Requirement Adherence (Score: 9/10)

**Strengths:**

- ✅ Input field for bill amount with proper number validation
- ✅ Tip percentage input with 15%, 18%, and 20% preset buttons
- ✅ Custom tip percentage input also available
- ✅ Instant calculation (reactive callbacks on all inputs)
- ✅ Displays tip amount and total bill
- ✅ Split among multiple people feature with per-person display
- ✅ No extra packages, no external CSS or JavaScript
- ✅ Screenshots confirm correct math: $85.50 × 20% = $17.10 tip, $102.60 total, $34.20/person
- ✅ Clean, professional interface visible in both screenshots

**Minor issues:**

- The active button highlight doesn't update when a preset is clicked (visual feedback is incomplete — "15%" always looks selected)
- The `tip_pct > 100` validation edge case returns an error even for values like 100, which is technically valid but unusual

---

MAINTAINABILITY_SCORE: 7
READABILITY_SCORE: 7
ADHERENCE_SCORE: 9