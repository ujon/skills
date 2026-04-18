---
name: css-design-system
description: >-
  Generate a CSS design-token styleguide for any web project — palette,
  typography scale, spacing, radius, light/dark theme, per-component CSS,
  and (by default) an HTML preview page. Ships seven design systems as
  ready-to-copy CSS blocks in references (Minimal, Material Design 3,
  Uber Base, IBM Carbon, Shopify Polaris, Radix Themes, Maximal); Claude
  assembles them into files directly (no build script). Use this skill
  whenever the user asks for CSS design tokens, CSS variables for a theme,
  a styleguide, a typography scale, a color palette, spacing/radius tokens,
  a preview of how a named design system looks, component CSS (`.btn`,
  `.input`, `.card`, etc.), or wants to apply / compare Minimal / Maximal /
  Material / Uber / Carbon / Polaris / Radix / Fluent / etc. Also use for
  "refresh the CSS tokens", "rebuild theme.css", "set up CSS variables",
  "show all sizes/colors on one page" — even if "styleguide" is never said.
  Project-agnostic; works for React, Vue, Svelte, Angular, or plain HTML/CSS.
---

# CSS Styleguide

Write a CSS design-token styleguide for any web project by assembling ready-to-copy blocks from `references/`. No build script — you write the files directly with the Write tool.

## What gets produced

```
<output>/
├── index.css              single import entry point — pulls in everything below, in order
├── primitives/
│   ├── palette.css        raw color tokens
│   ├── size.css           spacing, radius, button heights, transition
│   ├── typography.css     font family + six-step type scale
│   └── index.css          three-line import aggregator
├── theme.css              semantic mapping (light + dark)
├── extras.css             system-specific tokens (only if the system defines any)
├── components/            basic reusable components — always written
│   ├── button.css
│   ├── form.css           field + label + help + input + textarea + select + choice + switch
│   ├── badge.css
│   ├── avatar.css
│   ├── card.css
│   ├── alert.css
│   ├── progress.css
│   ├── tabs.css
│   ├── table.css
│   ├── link.css
│   └── index.css          aggregator
└── styleguide.html        self-contained preview — CSS inlined via <style> (preview only)
```

Consumers only need to import the top-level `index.css`; every other file is pulled in by its `@import` chain.

### Semantic tokens

Semantic token names are identical across all systems (`--bg`, `--fg`, `--space-md`, `--font-lg`, `--radius-md`, etc.). Only the values differ. System-specific tokens live in `extras.css` and never collide with the semantic layer.

### Basic components

The `components/` directory ships ten per-component stylesheets with plain class names that read only semantic tokens. Pick just the ones you need via `@import` — or import `components/index.css` for everything.

| File | Classes | Purpose |
|---|---|---|
| `button.css` | `.btn` + `.primary` / `.secondary` / `.ghost` / `.danger` / `.disabled` / `.sm` / `.lg` | Call-to-action buttons |
| `form.css` | `.field` / `.label` / `.input` / `.textarea` / `.select` / `.help` / `.choice` / `.switch` | Inputs + choice + toggle, with focus, error, disabled states |
| `badge.css` | `.badge` + solid / soft / outline / danger / success / warning | Labels + status chips |
| `avatar.css` | `.avatar` + `.accent` / `.lg` | User avatars |
| `card.css` | `.card` | Grouped content surface |
| `alert.css` | `.alert` + info / success / warning / danger | Inline banners |
| `progress.css` | `.progress` + `.progress-fill` | Linear progress |
| `tabs.css` | `.tabs` + `.tab` + `.active` | Tab bar |
| `table.css` | `.table` | Data tables |
| `link.css` | `.link` | Inline hyperlinks |

All classes swap correctly when the theme toggles and when the active design system is regenerated. If one of the plain names clashes with an existing class in the consumer's codebase, rename it with a single global search-and-replace before importing.

## When to trigger

User phrases:

- "make / generate a styleguide", "give me a style guide"
- "CSS design tokens", "CSS variables for my theme", "set up theme tokens"
- "typography scale", "color palette", "spacing scale", "radius tokens"
- "apply Material / Uber / Carbon / Polaris / Radix to this project"
- "compare design systems", "preview how X looks"
- "refresh / regenerate / reset the tokens / the theme"
- Any request that ends in writing CSS custom properties for a design system, even in scratch projects

Do not trigger for: editing one component's CSS, fixing a single style rule, or framework-specific build-config work.

## Workflow

### 1. Confirm the inputs

Ask the user (or infer from their message):

- **Which system?** One of: `minimal`, `material`, `uber-base`, `carbon`, `polaris`, `radix`, `maximal`. See `references/design-systems.md` for how to choose; default to `minimal` if unspecified.
- **Output directory?** Default: `styleguide-preview` relative to the current working directory.
- **Preview?** On by default. Skip preview files only if the user says things like "tokens only", "no preview", "skip preview", "no html", or "just the CSS".

### 2. Read only what you need

- Always: `references/<system>.md` — contains one code block per file to write.
- If preview is on: `references/preview.md` — shared HTML + CSS template + component examples.
- Only if the user is comparing systems or picking between them: `references/design-systems.md`.

Do not read references for systems you aren't generating.

### 3. Write the token files and components.css (always)

Copy blocks **verbatim** from `references/<system>.md`:

| Source block in reference | Write to |
|---|---|
| `## primitives/palette.css` | `<output>/primitives/palette.css` |
| `## primitives/size.css` | `<output>/primitives/size.css` |
| `## primitives/typography.css` | `<output>/primitives/typography.css` |
| `## theme.css` | `<output>/theme.css` |
| `## extras.css` (if present) | `<output>/extras.css` |

From `references/preview.md`:

| Source block | Write to |
|---|---|
| `## components/button.css` | `<output>/components/button.css` |
| `## components/form.css` | `<output>/components/form.css` |
| `## components/badge.css` | `<output>/components/badge.css` |
| `## components/avatar.css` | `<output>/components/avatar.css` |
| `## components/card.css` | `<output>/components/card.css` |
| `## components/alert.css` | `<output>/components/alert.css` |
| `## components/progress.css` | `<output>/components/progress.css` |
| `## components/tabs.css` | `<output>/components/tabs.css` |
| `## components/table.css` | `<output>/components/table.css` |
| `## components/link.css` | `<output>/components/link.css` |
| `## components/index.css` | `<output>/components/index.css` |

Always also write `<output>/primitives/index.css` with exactly:

```css
@import './palette.css';
@import './size.css';
@import './typography.css';
```

Don't invent values. If something looks wrong in the reference, fix the reference first and then regenerate.

The `components/` directory is written even when the user asks to skip the preview — components are part of "what the skill produces".

Finally, always write the top-level `<output>/index.css` — the single import entry point consumers use. Template:

```css
/*
 * Design system: {{SYSTEM_NAME}}
 * Generated by the css-design-system skill. Do not edit tokens here — edit
 * the per-layer files instead and this file will keep working.
 *
 * How to use
 *   1. Import this one file from your app stylesheet:
 *        @import 'styleguide-preview/index.css';
 *      — or link it from HTML:
 *        <link rel="stylesheet" href="styleguide-preview/index.css">
 *   2. Theme defaults to light. Toggle dark mode with:
 *        <html data-theme="dark">
 *      Remove the attribute (or set "light") to return to the default.
 *
 * Layers (imported in this order — later layers depend on earlier ones):
 *   primitives → theme → extras (if any) → components
 */

@import './primitives/index.css';
@import './theme.css';
@import './extras.css';
@import './components/index.css';
```

Replace `{{SYSTEM_NAME}}` with the chosen system's display name (from `## Preview metadata` → name in the system reference). If the system has no `extras.css`, omit the `@import './extras.css';` line entirely — do not leave a dangling import.

### 4. Write the preview (on by default)

If the user didn't ask to skip it, write a **single self-contained** `<output>/styleguide.html`. No separate `styleguide.css` file — all CSS lives in a `<style>` block inside the HTML so the preview opens directly from the filesystem with no link resolution.

Use the `## HTML template` from `references/preview.md`. Replace the `{{BUNDLED_CSS}}` placeholder with the following blocks concatenated in this exact order:

   1. `## Reset` from `references/preview.md`
   2. `## primitives/palette.css` from `references/<system>.md`
   3. `## primitives/size.css` from `references/<system>.md`
   4. `## primitives/typography.css` from `references/<system>.md`
   5. `## theme.css` from `references/<system>.md`
   6. `## extras.css` from `references/<system>.md` (if present)
   7. `## Base` from `references/preview.md`
   8. All ten `## components/*.css` blocks from `references/preview.md` (skip `index.css` — it's `@import`-only and those imports won't resolve inline)
   9. `## Preview chrome CSS` from `references/preview.md`

Then substitute the remaining placeholders per:

   | Placeholder | Source |
   |---|---|
   | `{{SYSTEM_NAME}}` | `## Preview metadata` → name, in the system reference |
   | `{{SYSTEM_DESCRIPTION}}` | `## Preview metadata` → description |
   | `{{TYPOGRAPHY_ROWS}}` | Mutually exclusive: if the system defines type roles (Material, Uber Base, Carbon, Maximal), emit one row per role; otherwise (Minimal, Polaris, Radix) emit six rows — one per `--font-xs` … `--font-2xl`. Never both. Patterns in preview.md. |
   | `{{SEMANTIC_SWATCHES}}` | One swatch div per key in the light `theme.css` `:root` block. |
   | `{{PRIMITIVE_SWATCHES}}` | One swatch div per palette primitive from the system. |
   | `{{SPACING_ROWS}}` | Five rows from the `--space-*` tokens. |
   | `{{RADIUS_BOXES}}` | Three boxes from `--radius-sm/md/lg`. |
   | `{{ELEVATION_SECTION}}` | Full section block if the system has elevation tokens, else empty string. |
   | `{{COMPONENTS_BLOCK}}` | Verbatim from `## Components HTML` in preview.md. |

### 5. If existing files would be overwritten

Check whether `<output>/` has content. If it does and the user hasn't said "overwrite", ask before proceeding. Never clobber silently.

### 6. Report

After writing, tell the user:
- The file paths written.
- The chosen system.
- Whether preview was included.
- How to open the preview (`open <output>/styleguide.html` on macOS, or equivalent).

## Invariants across systems

Every system's output contains these semantic tokens. Consumers can read them without caring which system was picked.

From `theme.css`: `--bg`, `--bg-subtle`, `--bg-muted`, `--bg-elevated`, `--fg`, `--fg-muted`, `--fg-subtle`, `--border`, `--border-strong`, `--accent`, `--accent-muted`, `--highlight`, `--highlight-muted`, `--danger`, `--success`, `--warning`.

From primitives: `--font-sans`, `--font-mono`, `--font-xs` … `--font-2xl`, `--space-xs` … `--space-xl`, `--radius-sm/md/lg`, `--btn-sm/md/lg`, `--transition`.

Everything else is a system-specific extra — keep it in `extras.css`.

## Adding a new system

If the user wants a system not in the list (Fluent, Ant Design, Atlassian, Tailwind defaults, custom house style…):

1. Add `references/<new-system>.md` using the same section structure as the existing six files: palette / size / typography / theme / extras / Preview metadata / Source.
2. Pull values from the upstream spec; note the source URL.
3. Run the same workflow against the new reference.

Keep the semantic token names identical — only values and extras change per system.

## References

- `references/design-systems.md` — selection guide and invariants.
- `references/preview.md` — shared reset + base + preview CSS + HTML template + components block.
- `references/<system>.md` × 6 — per-system CSS blocks, one per file.

## What this skill does not do

- **No automatic project integration.** The output sits in the directory you pass. Wiring is one line: `@import '<output>/index.css';` from a root stylesheet (or a `<link>` tag in HTML). The top-level `index.css` chains primitives → theme → extras → components for you.
- **No script runner.** Generation is manual — open references, write files. Keeps the skill light and transparent.
- **No namespace guarantee.** `components/` uses plain class names (`.btn`, `.input`, `.card`, …). If any clash with your codebase, rename via global search-and-replace before importing.
