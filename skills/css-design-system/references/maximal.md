# Maximal

The counterpart to Minimal. Where Minimal strips ornament, Maximal embraces it: vivid purple brand accent, extended typography hierarchy (27 named roles across Display / Headline / Title / Body / Caption / Button), a generous 18-step spacing ladder, two-level shadow, and overlay dim for modal chrome. Good fit for marketing sites, content-heavy apps, or any product that wants the UI to feel distinct rather than quiet.

## primitives/palette.css

```css
:root {
	/* Brand */
	--brand-main: #6100FF;
	--brand-sub-1: #39C3B6;
	--brand-sub-2: #F59917;

	/* Foreground — four-step hierarchy */
	--fg-color-main: #111111;
	--fg-color-sub-1: #505050;
	--fg-color-sub-2: #767676;
	--fg-color-disabled: #999999;

	/* Line */
	--line-light: #F1F1F5;
	--line-medium: #E5E5EC;
	--line-strong: #111111;

	/* Background */
	--bg-light: #F7F7FB;
	--bg-strong: #F1F1F5;

	/* Status */
	--status-danger: #DC0000;
	--status-success: #04B014;
	--status-warning: #FFAA00;

	/* Base */
	--white: #FFFFFF;
	--black: #000000;

	/* Dark-mode neutrals */
	--dark-bg: #111111;
	--dark-bg-subtle: #1A1A1A;
	--dark-bg-muted: #222222;
	--dark-bg-elevated: #2A2A2A;
	--dark-fg: #FFFFFF;
	--dark-fg-muted: #C8C8C8;
	--dark-fg-subtle: #8A8A8A;
	--dark-border: #333333;
	--dark-border-strong: #555555;
	--dark-accent-muted: #2A0F5E;
}
```

## primitives/size.css

```css
:root {
	/* Spacing — semantic subset. Full 18-step ladder in extras.css */
	--space-xs: 4px;
	--space-sm: 8px;
	--space-md: 16px;
	--space-lg: 24px;
	--space-xl: 40px;

	/* Button size — three hierarchy levels */
	--btn-sm: 40px;
	--btn-md: 48px;
	--btn-lg: 56px;

	/* Radius */
	--radius-sm: 4px;
	--radius-md: 8px;
	--radius-lg: 16px;

	/* Transition */
	--transition: 150ms ease;
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: 'Inter', 'SF Pro Text', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	--font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace;

	/* Font size — six semantic steps */
	--font-xs: 12px;
	--font-sm: 13px;
	--font-md: 15px;
	--font-lg: 18px;
	--font-xl: 24px;
	--font-2xl: 32px;

	/* Default tracking */
	--letter-spacing-tight: -0.025em;
	--letter-spacing-normal: 0;
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--white);
	--bg-subtle: var(--bg-light);
	--bg-muted: var(--bg-strong);
	--bg-elevated: var(--line-medium);

	--fg: var(--fg-color-main);
	--fg-muted: var(--fg-color-sub-1);
	--fg-subtle: var(--fg-color-sub-2);

	--border: var(--line-medium);
	--border-strong: var(--line-strong);

	--accent: var(--brand-main);
	--accent-muted: color-mix(in srgb, var(--brand-main) 12%, transparent);

	--highlight: var(--brand-main);
	--highlight-muted: color-mix(in srgb, var(--brand-main) 10%, transparent);

	--danger: var(--status-danger);
	--success: var(--status-success);
	--warning: var(--status-warning);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--dark-bg);
	--bg-subtle: var(--dark-bg-subtle);
	--bg-muted: var(--dark-bg-muted);
	--bg-elevated: var(--dark-bg-elevated);

	--fg: var(--dark-fg);
	--fg-muted: var(--dark-fg-muted);
	--fg-subtle: var(--dark-fg-subtle);

	--border: var(--dark-border);
	--border-strong: var(--dark-border-strong);

	--accent: #8E4BFF;
	--accent-muted: var(--dark-accent-muted);

	--highlight: #8E4BFF;
	--highlight-muted: var(--dark-accent-muted);

	--danger: #FF6A5E;
	--success: #52C785;
	--warning: #FFC453;
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--dark-bg);
		--bg-subtle: var(--dark-bg-subtle);
		--bg-muted: var(--dark-bg-muted);
		--bg-elevated: var(--dark-bg-elevated);

		--fg: var(--dark-fg);
		--fg-muted: var(--dark-fg-muted);
		--fg-subtle: var(--dark-fg-subtle);

		--border: var(--dark-border);
		--border-strong: var(--dark-border-strong);

		--accent: #8E4BFF;
		--accent-muted: var(--dark-accent-muted);

		--highlight: #8E4BFF;
		--highlight-muted: var(--dark-accent-muted);

		--danger: #FF6A5E;
		--success: #52C785;
		--warning: #FFC453;
	}
}
```

## extras.css

```css
:root {
	/* Extended spacing ladder */
	--space-scale-2: 2px;
	--space-scale-4: 4px;
	--space-scale-8: 8px;
	--space-scale-12: 12px;
	--space-scale-16: 16px;
	--space-scale-20: 20px;
	--space-scale-24: 24px;
	--space-scale-28: 28px;
	--space-scale-32: 32px;
	--space-scale-40: 40px;
	--space-scale-48: 48px;
	--space-scale-60: 60px;
	--space-scale-70: 70px;
	--space-scale-80: 80px;
	--space-scale-100: 100px;
	--space-scale-120: 120px;
	--space-scale-140: 140px;
	--space-scale-180: 180px;

	/* Display roles */
	--typography-display-1-size: 56px;
	--typography-display-1-line: 72px;
	--typography-display-1-tracking: -0.025em;
	--typography-display-2-size: 48px;
	--typography-display-2-line: 62px;
	--typography-display-2-tracking: -0.025em;
	--typography-display-3-size: 40px;
	--typography-display-3-line: 52px;
	--typography-display-3-tracking: -0.025em;
	--typography-display-4-size: 36px;
	--typography-display-4-line: 44px;
	--typography-display-4-tracking: -0.025em;
	--typography-display-5-size: 32px;
	--typography-display-5-line: 42px;
	--typography-display-5-tracking: -0.025em;
	--typography-display-6-size: 28px;
	--typography-display-6-line: 38px;
	--typography-display-6-tracking: -0.025em;

	/* Headline roles */
	--typography-headline-1-size: 32px;
	--typography-headline-1-line: 42px;
	--typography-headline-2-size: 28px;
	--typography-headline-2-line: 38px;
	--typography-headline-3-size: 24px;
	--typography-headline-3-line: 34px;
	--typography-headline-4-size: 20px;
	--typography-headline-4-line: 28px;
	--typography-headline-5-size: 18px;
	--typography-headline-5-line: 26px;
	--typography-headline-6-size: 16px;
	--typography-headline-6-line: 24px;

	/* Title roles */
	--typography-title-1-size: 24px;
	--typography-title-1-line: 34px;
	--typography-title-2-size: 20px;
	--typography-title-2-line: 28px;
	--typography-title-3-size: 18px;
	--typography-title-3-line: 26px;
	--typography-title-4-size: 16px;
	--typography-title-4-line: 24px;

	/* Body roles */
	--typography-body-1-size: 15px;
	--typography-body-1-line: 22px;
	--typography-body-2-size: 14px;
	--typography-body-2-line: 20px;
	--typography-body-3-size: 13px;
	--typography-body-3-line: 18px;
	--typography-body-4-size: 12px;
	--typography-body-4-line: 18px;

	/* Caption roles */
	--typography-caption-1-size: 13px;
	--typography-caption-1-line: 18px;
	--typography-caption-2-size: 12px;
	--typography-caption-2-line: 18px;
	--typography-caption-3-size: 11px;
	--typography-caption-3-line: 16px;

	/* Button labels */
	--typography-button-1-size: 16px;
	--typography-button-1-line: 24px;
	--typography-button-2-size: 14px;
	--typography-button-2-line: 20px;
	--typography-button-3-size: 13px;
	--typography-button-3-line: 18px;
	--typography-button-4-size: 12px;
	--typography-button-4-line: 18px;

	/* Elevation — two levels */
	--elevation-1: 0 2px 8px rgba(17, 17, 17, 0.06), 0 1px 2px rgba(17, 17, 17, 0.04);
	--elevation-2: 0 8px 24px rgba(17, 17, 17, 0.10), 0 2px 6px rgba(17, 17, 17, 0.06);

	/* Overlay dim for modal chrome */
	--overlay-dim: rgba(0, 0, 0, 0.6);

	/* Icon defaults */
	--icon-size: 24px;
	--icon-stroke: 2px;
	--icon-color-main: var(--fg-color-main);
	--icon-color-sub-1: var(--fg-color-sub-1);
	--icon-color-sub-2: var(--fg-color-sub-2);
	--icon-color-disabled: var(--fg-color-disabled);
	--icon-color-inverted: var(--white);
}
```

## Preview metadata

- **name**: Maximal
- **description**: Expressive counterpart to Minimal — vivid purple brand, 27 type roles, extended spacing ladder, shadow-heavy chrome.
- **type_roles**: emit (size / line / weight):
  - display-1 · 56px · 72px · 600
  - display-2 · 48px · 62px · 600
  - display-3 · 40px · 52px · 600
  - display-4 · 36px · 44px · 600
  - display-5 · 32px · 42px · 600
  - display-6 · 28px · 38px · 600
  - headline-1 · 32px · 42px · 600
  - headline-2 · 28px · 38px · 600
  - headline-3 · 24px · 34px · 600
  - headline-4 · 20px · 28px · 600
  - headline-5 · 18px · 26px · 600
  - headline-6 · 16px · 24px · 600
  - title-1 · 24px · 34px · 600
  - title-2 · 20px · 28px · 600
  - title-3 · 18px · 26px · 600
  - title-4 · 16px · 24px · 600
  - body-1 · 15px · 22px · 400
  - body-2 · 14px · 20px · 400
  - body-3 · 13px · 18px · 400
  - body-4 · 12px · 18px · 400
  - caption-1 · 13px · 18px · 400
  - caption-2 · 12px · 18px · 400
  - caption-3 · 11px · 16px · 400
  - button-1 · 16px · 24px · 600
  - button-2 · 14px · 20px · 600
  - button-3 · 13px · 18px · 600
  - button-4 · 12px · 18px · 600
- **elevation**: emit section with `--elevation-1`, `--elevation-2`.

## Source

In-house. The richest of the bundled systems: 27 type roles, 18-step spacing, explicit elevation, icon defaults, and overlay dim. Use when Minimal feels too quiet and you want every chrome element to have an opinion.
