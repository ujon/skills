# Design Systems — Selection Guide

Seven systems ship with the generator. All emit the same **semantic token names** — only the values and system-specific extras change. This means a consumer that reads `var(--fg)` or `var(--font-md)` keeps working when the system is swapped.

## Quick table

| Key | Name | Font stack | Personality |
|---|---|---|---|
| `minimal` | Minimal | System UI | Monochrome, quiet, tooling-friendly baseline |
| `material` | Material Design 3 | Roboto | Expressive, tonal, consumer product |
| `uber-base` | Uber Base | UberMove → system | Data-dense, mono-heavy, tight radii |
| `carbon` | IBM Carbon v11 | IBM Plex Sans | Enterprise, sharp, high-contrast, disciplined type |
| `polaris` | Shopify Polaris | Inter | Commerce, soft rounded, friendly |
| `radix` | Radix Themes | Inter / system | Developer UI, 12-step scales, neutral + crisp accent |
| `maximal` | Maximal | Inter | Expressive counterpart to Minimal — vivid purple brand, 27 type roles, 18-step spacing ladder, shadow-heavy chrome |

## How to pick

Walk through these in order:

1. **Is this a refresh or a redesign?**
   - Refresh of an existing monochrome look → `minimal`.
   - New identity → everything else is on the table.
2. **Consumer product, or internal / B2B tool?**
   - Consumer, expressive → `material` or `polaris`.
   - Internal, data-heavy → `uber-base`, `carbon`, or `radix`.
3. **Do you need strict enterprise contrast and accessibility defaults?**
   - Yes → `carbon` (IBM's a11y rigor is baked in) or `polaris`.
4. **Is the accent color negotiable?**
   - Radix and Carbon are easy to re-skin (swap a single primitive ramp).
   - Uber Base's identity *is* Uber blue; swapping it weakens the feel.
5. **Developer tool vs. end-user UI?**
   - Developer → `radix` (scales were designed for app chrome) or `minimal`.
   - End-user → `material`, `polaris`.

If the user has no preference, default to `minimal`, generate, let them see it, and offer to regenerate with another system.

## Semantic invariants (same across all systems)

These tokens always exist. Consumers can rely on them.

**From `theme.css` (light + dark):**

| Token | Role |
|---|---|
| `--bg` | App background |
| `--bg-subtle` | Surface level 1 (cards, panels) |
| `--bg-muted` | Surface level 2 (raised) |
| `--bg-elevated` | Surface level 3 (pop-outs) |
| `--fg` | Default text color |
| `--fg-muted` | Secondary text |
| `--fg-subtle` | Tertiary text, placeholders |
| `--border` | Default border |
| `--border-strong` | Emphasized border |
| `--accent` | Brand / primary action color |
| `--accent-muted` | Hover / container variant of accent |
| `--highlight` | Links, focus |
| `--highlight-muted` | Focus container |
| `--danger` | Error / destructive |
| `--success` | Success / positive |
| `--warning` | Warning / caution |

**From `primitives/typography.css`:**

| Token | Role |
|---|---|
| `--font-sans` | Default sans font stack |
| `--font-mono` | Code / tabular |
| `--font-xs` | Smallest text (11–12px) |
| `--font-sm` | Secondary UI text (13–14px) |
| `--font-md` | Body default (15–16px) |
| `--font-lg` | Section headings (18–22px) |
| `--font-xl` | Page headings (24–28px) |
| `--font-2xl` | Hero headings (32–40px) |

**From `primitives/size.css`:**

| Token | Role |
|---|---|
| `--space-xs` … `--space-xl` | 4/8/16/24/40 (or close) |
| `--radius-sm`, `--radius-md`, `--radius-lg` | Small / medium / large corners |
| `--btn-sm`, `--btn-md`, `--btn-lg` | Button heights |
| `--transition` | Default motion |

## What changes per system

Per system, only:

- **Values** of the semantic tokens above.
- **Primitive palette** — Minimal uses a gray scale; Material uses MD3 tonal ramps; Uber uses mono + Uber blue; Carbon uses IBM gray + IBM blue; Polaris uses a neutral scale + brand; Radix uses slate + a chosen accent scale.
- **Extras** — Material adds `--md-elevation-*`, `--md-shape-*`, `--typography-<role>-*`; Uber adds `--typography-<role>-*`; Carbon adds the 16-step gray scale and Carbon type role sizes; Polaris adds Polaris's size tokens (025 through 1000); Radix adds 12-step scales.

## Anti-patterns

- **Renaming semantic tokens to match a system's native vocabulary.** MD3 calls foreground "on-surface"; that name is available as an extra, but `--fg` is what consumers read. Don't rename.
- **Mixing systems in one `theme.css`.** If the user wants Material typography with Uber colors, treat it as a new system (`custom-hybrid`) with its own reference file and entry in `SYSTEMS`.
- **Dropping the six semantic type steps.** Every system maps its roles onto `--font-xs` through `--font-2xl`. Consumers that read those names must keep working.
- **Hard-coding a theme's background or foreground in a component.** Components should read `var(--fg)` / `var(--bg)`, never `#000` / `#fff` or the primitive palette names. That's how system-swap stays free.

## Source notes

Each reference file names its source (URL, spec version, license). The token values captured here are best-effort distillations sized for a six-step scale; exact fidelity to the upstream system is not guaranteed and the user should verify before shipping.
