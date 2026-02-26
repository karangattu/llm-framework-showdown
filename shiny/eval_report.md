I'll evaluate this Shiny for Python tip calculator app on the three criteria.

#### Criterion 1: Maintainability (Score: 9/10)

**Strengths:**

- Well-structured separation between UI and server logic with clear section comments
- Single `calc()` reactive that centralizes all computation — easy to modify formulas in one place
- Logical grouping of UI elements into cards (inputs, results, split)
- Preset button handlers are clean and consistent (three separate `@reactive.effect` handlers)
- Good use of `max(int(...), 1)` guard to prevent division by zero
- Named outputs are clearly mapped to their display elements

**Minor concerns:**

- The three preset handlers are slightly repetitive; a helper function could reduce boilerplate, but at this scale it's acceptable
- The `calc()` dictionary approach works but a dataclass/namedtuple would be more maintainable at larger scale

#### Criterion 2: Readability (Score: 9/10)

**Strengths:**

- Excellent use of section comments (`# ── Header ──`, `# ── Server ──`, etc.) for visual scanning
- Variable names (`bill`, `tip_pct`, `num_people`, `per_person_tip`) are highly descriptive
- Follows idiomatic Shiny for Python patterns (`@reactive.calc`, `@render.text`, `@reactive.effect`)
- The UI structure mirrors what the user sees, making it easy to map code to visual output
- Arithmetic is straightforward and easy to follow

**Minor concerns:**

- `_apply_15`, `_apply_18`, `_apply_20` private naming convention is fine but the underscore prefix may confuse some readers
- A brief comment explaining the `or 0.0` / `or 1` fallback pattern would help

#### Criterion 3: Requirement Adherence (Score: 10/10)

**Strengths:**

- ✅ Input field for bill amount (numeric, default $50, step $0.01)
- ✅ Input field for tip percentage (numeric, editable)
- ✅ All three presets present: 15%, 18%, 20% as action buttons
- ✅ Instant calculation (reactive, no submit button needed)
- ✅ Displays tip amount ($17.10 for $85.50 × 20% ✓)
- ✅ Displays total bill ($102.60 = $85.50 + $17.10 ✓)
- ✅ Bill splitting among N people ($34.20 = $102.60 ÷ 3 ✓)
- ✅ No external CSS, JavaScript, or extra packages used
- ✅ Screenshots confirm correct calculations for the test case
- The bonus "split tip only" per person is a nice addition

All calculations verified against the after screenshot are mathematically correct.
