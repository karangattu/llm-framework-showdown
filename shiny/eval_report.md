I'll evaluate the app on the three criteria by analyzing the code and screenshots.

#### Criterion 1: Maintainability (1-10)

**Strengths:**

- Good separation of concerns: UI definition, reactive calculations, and rendering are clearly separated
- The `calculations()` reactive calc centralizes all math logic into one function returning a dictionary — easy to extend
- `tip_percentage()` is a separate reactive calc, showing good decomposition
- The two-column layout using `layout_columns` is clean and scalable
- Adding new tip presets or calculation fields would be straightforward

**Weaknesses:**

- The `results()` renderer builds HTML tables manually with lots of repetitive `ui.tags.tr/td` calls — this could be factored into a helper function
- Inline styles scattered throughout the render function make style changes tedious
- The split section logic is somewhat intertwined with the main table-building logic

**Score: 7/10**

#### Criterion 2: Readability (1-10)

**Strengths:**

- Variable names are clear and descriptive (`bill_amount`, `tip_percentage`, `tip_per_person`, etc.)
- The reactive chain is easy to follow: inputs → `tip_percentage()` → `calculations()` → `results()`
- The dictionary returned from `calculations()` is self-documenting
- Idiomatic Shiny for Python patterns are used throughout (`@reactive.calc`, `@render.ui`, etc.)
- The conditional panel usage for "Custom" tip is a clean idiom

**Weaknesses:**

- The `results()` function is quite long due to manual HTML construction — a helper like `make_row(label, value)` would improve readability
- No comments explaining the overall structure or any non-obvious decisions
- The inline styles within tags make the rendering code visually dense

**Score: 7/10**

#### Criterion 3: Requirement Adherence (1-10)

**Strengths:**

- ✅ Input fields for bill amount and tip percentage
- ✅ All three presets (15%, 18%, 20%) present as radio buttons plus a Custom option
- ✅ Instantly calculates and displays tip amount and total bill (reactive)
- ✅ Splits total among multiple people with per-person breakdown
- ✅ No extra packages, CSS files, or JavaScript beyond Shiny's built-ins (inline styles use Shiny's tag system)
- ✅ Screenshots confirm correct calculations: $85.50 × 20% = $17.10 tip, $102.60 total, $34.20 per person, $5.70 tip per person — all accurate
- ✅ Split details section appears conditionally only when people > 1

**Minor concerns:**

- The "custom tip" adds extra functionality beyond the strict requirement but doesn't detract
- Input numeric shows `50.0` in the before screenshot (minor display quirk)

**Score: 10/10**

---

MAINTAINABILITY_SCORE: 7
READABILITY_SCORE: 7
ADHERENCE_SCORE: 10