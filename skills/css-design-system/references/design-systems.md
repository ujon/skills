# Design Systems — Selection Guide

Five systems ship with the generator. All emit the same **internal semantic token names** — only the values and system-specific extras change. Consumers interact through classes in `components/`; the tokens are an implementation detail. Because every system's `components/` classes read the same invariant tokens, swapping systems keeps consumer markup working unchanged (only typography class vocabulary differs per system; see below).

## Quick table

| Key | Name | Font stack | Personality |
|---|---|---|---|
| `minimal` | Minimal | System UI | Monochrome, quiet, tooling-friendly baseline |
| `material` | Material Design 3 | Roboto | Expressive, tonal, consumer product; full type + shape + elevation scales |
| `carbon` | IBM Carbon v11 | IBM Plex Sans | Enterprise, sharp, high-contrast, disciplined type |
| `fluent` | Microsoft Fluent 2 | Segoe UI Variable | Windows / Microsoft 365 feel; Communication Blue, two-layer elevation, full Fluent motion ramp |
| `maximal` | Maximal | Inter | Expressive counterpart to Minimal — vivid purple brand, 27 type roles, 18-step spacing ladder, shadow-heavy chrome |

## How to pick

Walk through these in order:

1. **Is this a refresh or a redesign?**
   - Refresh of an existing monochrome look → `minimal`.
   - New identity → everything else is on the table.
2. **Platform / ecosystem fit?**
   - Windows / Microsoft 365 surface area → `fluent` (Segoe UI Variable + Communication Blue ties the bundle to the Microsoft visual language).
   - Google / Android / cross-platform consumer → `material`.
   - Enterprise, IBM-adjacent, or a11y-first → `carbon`.
   - Brand-forward, expressive, AI-vibe / landing-page energy → `maximal`.
3. **How much motion and elevation do you need?**
   - Rich motion + layered elevation → `material` (MD3 motion + elevation scales) or `fluent` (Fluent durations + easing curves + two-layer shadows).
   - Flat, minimal chrome → `minimal` or `carbon`.
4. **Is the accent color negotiable?**
   - `minimal`, `carbon`, and `maximal` re-skin easily (swap `--accent` and its container token in `theme.css`).
   - `material` and `fluent` have recognizable brand colors (MD3 tonal + Communication Blue); swapping weakens the visual identity but is still possible.
5. **Type vocabulary you want in markup?**
   - Few, uniform sizes (6-step `.text-*`) → `minimal`.
   - MD3 `.display-*` / `.headline-*` / `.body-*` / `.label-*` → `material`.
   - Carbon productive `.body-01`, `.heading-01`..`.heading-07` → `carbon`.
   - Fluent `.caption1`, `.body1`, `.subtitle1`, `.title1`..`.title3`, `.large-title`, `.display` → `fluent`.
   - 27 named roles (display / headline / title / body / caption / button) → `maximal`.

If the user has no preference, default to `minimal`, generate, let them see it, and offer to regenerate with another system.

## Semantic invariants (same across all systems)

These tokens always exist inside the bundle and are consumed by `components/` classes. They are *not* part of the public API — consumers apply classes, not variables — but anyone adding a new system must keep this naming stable so the system-agnostic component files continue to work.

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
| `--font-xs` | Smallest text (10–12px) |
| `--font-sm` | Secondary UI text (13–14px) |
| `--font-md` | Body default (15–16px) |
| `--font-lg` | Section headings (18–22px) |
| `--font-xl` | Page headings (24–28px) |
| `--font-2xl` | Hero headings (32–40px) |

**From `primitives/size.css`:**

| Token | Role |
|---|---|
| `--space-xs` … `--space-xl` | 4/8/12–16/20–24/32–40 (system-specific) |
| `--radius-sm`, `--radius-md`, `--radius-lg` | Small / medium / large corners |
| `--btn-sm`, `--btn-md`, `--btn-lg` | Button heights |
| `--transition` | Default motion |

## What changes per system

Per system, only:

- **Values** of the semantic tokens above.
- **Primitive palette** — Minimal uses a gray scale + accents; Material uses MD3 tonal ramps; Carbon uses IBM 16-step gray + IBM blue; Fluent uses the 50-step Fluent grey ramp + Communication Blue; Maximal uses a custom brand + 12-step warm neutrals.
- **Tokens inside `primitives/*.css`** — each system declares its own full set in the concern-named primitive file:
  - `palette.css` — every color token (Carbon's 16-step gray + blue, Material's tonal ramps, Fluent's grey+blue ramps, etc.).
  - `size.css` — every dimension token (the semantic `--space-*/--radius-*/--btn-*/--transition` invariants *plus* any extensions: Maximal's 18-step `--space-scale-*`, Material's `--md-shape-*`, Fluent's full corner + spacing + stroke scales, icon sizing, etc.).
  - `typography.css` — every type token (semantic `--font-*` invariants *plus* every `--typography-<role>-*` for systems that have roles).
  - `motion.css` *(optional)* — motion tokens beyond `--transition`. Material ships MD3 easings + durations; Fluent ships Fluent 2 durations (ultrafast → ultraslow) and easing curves; Minimal / Carbon / Maximal skip the file.
  - `effects.css` *(optional)* — shadows / elevation / glow / gradient tokens. Material ships MD3 elevation (`--elevation-0..5`); Fluent ships two-layer shadows (`--shadow-2/4/8/16/28/64`, light + dark variants); Maximal ships `--elevation-1/2`. Minimal and Carbon skip the file.
- **`theme.css`** absorbs any *semantic color-role mappings* — including overlay-dim and icon-color-* for systems that define them. They belong with `--bg` / `--fg` semantics, not with raw color primitives.
- **Typography class vocabulary** (`components/typography.css`) — Minimal emits `.text-xs` … `.text-2xl`; every other system emits one class per role (e.g. `.display-large`, `.heading-01`, `.body1`). Mutually exclusive per system — a bundle ships one or the other, never both.
- **Color class vocabulary** (`components/color.css`) — **identical across every system**. Wraps every non-default semantic role (`--bg-subtle`, `--accent`, `--danger`, …) as `.bg-*` / `.text-*` / `.border-*` utilities. Default roles (`--bg` / `--fg` / `--border`) apply via the body reset and need no class. Dark mode follows automatically because the classes only read `var(--*)`.
- **`components/effects.css`** *(optional)* — effect classes like `.glow` / `.sweep` / `.glow-sweep` plus their `@keyframes` and reduced-motion overrides. Ships only with systems that expose such effects (today: a custom extension on top of Maximal).

There is no `extras.css`. Every token and every class has a concern-named home.

## Anti-patterns

- **Renaming semantic tokens to match a system's native vocabulary.** MD3 calls foreground "on-surface"; Fluent calls it "colorNeutralForeground1". Those names live inside the per-system `typography.css` / `theme.css` as implementation details, but `--fg` is what consumer-facing classes read. Don't rename the invariants.
- **Mixing systems in one `theme.css`.** If the user wants Material typography with Fluent colors, treat it as a new system (`custom-hybrid`) with its own reference file and entry in the selection list.
- **Dropping the `--font-xs` … `--font-2xl` scale.** Every system's `primitives/typography.css` defines the six steps — Minimal's `.text-*` classes and the preview chrome read from them. Don't remove them even for systems that also expose per-role tokens.
- **Hard-coding a theme color inside a component class.** Component class files must read `var(--fg)` / `var(--bg)`, never `#000` / `#fff` or primitive palette names. That's how system-swap stays free.
- **Reading variables from consumer code.** `var(--accent)` in an app's own stylesheet is outside the public API — apply a component class instead, or add a new component file inside this bundle if a gap exists.

## Source notes

Each reference file names its source (URL, spec version, license). The token values captured here are best-effort distillations sized for the invariant scale; exact fidelity to the upstream system is not guaranteed and the user should verify before shipping.
