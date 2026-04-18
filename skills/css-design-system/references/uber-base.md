# Uber Base

Uber's open-source design system (Base Web). Mono-heavy palette + one Uber blue accent, tight radii. Data-dense product UI, tables, dashboards.

## primitives/palette.css

```css
:root {
	--mono-0: #FFFFFF;
	--mono-100: #F6F6F6;
	--mono-200: #EEEEEE;
	--mono-300: #E2E2E2;
	--mono-400: #CBCBCB;
	--mono-500: #AFAFAF;
	--mono-600: #6B6B6B;
	--mono-700: #545454;
	--mono-800: #333333;
	--mono-900: #1F1F1F;
	--mono-1000: #000000;

	--accent-50: #EFF3FE;
	--accent-100: #D4E2FC;
	--accent-300: #5B91F5;
	--accent-400: #276EF1;
	--accent-500: #1E54B7;
	--accent-700: #0E326C;

	--positive-100: #E6F2EC;
	--positive-400: #07823F;
	--negative-100: #FFEFED;
	--negative-400: #E11900;
	--warning-100: #FFF3D6;
	--warning-400: #FFC043;
}
```

## primitives/size.css

```css
:root {
	/* Spacing */
	--space-xs: 4px;
	--space-sm: 8px;
	--space-md: 16px;
	--space-lg: 24px;
	--space-xl: 40px;

	/* Button size */
	--btn-sm: 32px;
	--btn-md: 40px;
	--btn-lg: 48px;

	/* Radius — Base is tight */
	--radius-sm: 2px;
	--radius-md: 4px;
	--radius-lg: 8px;

	/* Transition */
	--transition: 150ms cubic-bezier(0, 0, 1, 1);
}
```

## primitives/typography.css

```css
:root {
	/* Font family — UberMove with system fallback */
	--font-sans: 'UberMoveText', 'UberMove', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	--font-mono: 'UberMoveMono', 'SF Mono', 'Menlo', monospace;

	/* Font size — mapped to Base roles */
	--font-xs: 12px;  /* ParagraphXSmall / LabelXSmall */
	--font-sm: 14px;  /* ParagraphSmall / LabelMedium */
	--font-md: 16px;  /* ParagraphMedium / LabelLarge */
	--font-lg: 20px;  /* HeadingSmall */
	--font-xl: 28px;  /* HeadingLarge */
	--font-2xl: 36px; /* HeadingXXLarge */
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--mono-0);
	--bg-subtle: var(--mono-100);
	--bg-muted: var(--mono-200);
	--bg-elevated: var(--mono-300);

	--fg: var(--mono-1000);
	--fg-muted: var(--mono-700);
	--fg-subtle: var(--mono-600);

	--border: var(--mono-400);
	--border-strong: var(--mono-500);

	--accent: var(--accent-400);
	--accent-muted: var(--accent-100);

	--highlight: var(--accent-400);
	--highlight-muted: var(--accent-50);

	--danger: var(--negative-400);
	--success: var(--positive-400);
	--warning: var(--warning-400);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--mono-1000);
	--bg-subtle: var(--mono-900);
	--bg-muted: var(--mono-800);
	--bg-elevated: var(--mono-700);

	--fg: var(--mono-0);
	--fg-muted: var(--mono-400);
	--fg-subtle: var(--mono-500);

	--border: var(--mono-700);
	--border-strong: var(--mono-600);

	--accent: var(--accent-300);
	--accent-muted: var(--accent-700);

	--highlight: var(--accent-300);
	--highlight-muted: var(--accent-700);

	--danger: #FF5C4A;
	--success: #55B583;
	--warning: #FFD27F;
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--mono-1000);
		--bg-subtle: var(--mono-900);
		--bg-muted: var(--mono-800);
		--bg-elevated: var(--mono-700);

		--fg: var(--mono-0);
		--fg-muted: var(--mono-400);
		--fg-subtle: var(--mono-500);

		--border: var(--mono-700);
		--border-strong: var(--mono-600);

		--accent: var(--accent-300);
		--accent-muted: var(--accent-700);

		--highlight: var(--accent-300);
		--highlight-muted: var(--accent-700);

		--danger: #FF5C4A;
		--success: #55B583;
		--warning: #FFD27F;
	}
}
```

## extras.css

```css
:root {
	/* Base type roles */
	--typography-display-large-size: 60px;
	--typography-display-large-line: 68px;
	--typography-display-large-weight: 800;
	--typography-display-medium-size: 48px;
	--typography-display-medium-line: 56px;
	--typography-display-medium-weight: 800;
	--typography-display-small-size: 38px;
	--typography-display-small-line: 44px;
	--typography-display-small-weight: 800;

	--typography-heading-xxlarge-size: 36px;
	--typography-heading-xxlarge-line: 44px;
	--typography-heading-xxlarge-weight: 500;
	--typography-heading-xlarge-size: 32px;
	--typography-heading-xlarge-line: 40px;
	--typography-heading-xlarge-weight: 500;
	--typography-heading-large-size: 28px;
	--typography-heading-large-line: 36px;
	--typography-heading-large-weight: 500;
	--typography-heading-medium-size: 24px;
	--typography-heading-medium-line: 32px;
	--typography-heading-medium-weight: 500;
	--typography-heading-small-size: 20px;
	--typography-heading-small-line: 28px;
	--typography-heading-small-weight: 500;
	--typography-heading-xsmall-size: 16px;
	--typography-heading-xsmall-line: 24px;
	--typography-heading-xsmall-weight: 500;

	--typography-paragraph-large-size: 18px;
	--typography-paragraph-large-line: 28px;
	--typography-paragraph-large-weight: 400;
	--typography-paragraph-medium-size: 16px;
	--typography-paragraph-medium-line: 24px;
	--typography-paragraph-medium-weight: 400;
	--typography-paragraph-small-size: 14px;
	--typography-paragraph-small-line: 20px;
	--typography-paragraph-small-weight: 400;
	--typography-paragraph-xsmall-size: 12px;
	--typography-paragraph-xsmall-line: 20px;
	--typography-paragraph-xsmall-weight: 400;

	--typography-label-large-size: 16px;
	--typography-label-large-line: 20px;
	--typography-label-large-weight: 500;
	--typography-label-medium-size: 14px;
	--typography-label-medium-line: 16px;
	--typography-label-medium-weight: 500;
	--typography-label-small-size: 14px;
	--typography-label-small-line: 16px;
	--typography-label-small-weight: 500;
	--typography-label-xsmall-size: 12px;
	--typography-label-xsmall-line: 16px;
	--typography-label-xsmall-weight: 500;

	/* Elevation */
	--shadow-1: 0 1px 4px rgba(0, 0, 0, 0.16);
	--shadow-2: 0 4px 12px rgba(0, 0, 0, 0.18);
}
```

## Preview metadata

- **name**: Uber Base
- **description**: UberMove/system, mono-heavy + Uber blue, tight radii. Data-dense.
- **type_roles**: emit:
  - display-large · 60px · 68px · 800
  - display-medium · 48px · 56px · 800
  - display-small · 38px · 44px · 800
  - heading-xxlarge · 36px · 44px · 500
  - heading-xlarge · 32px · 40px · 500
  - heading-large · 28px · 36px · 500
  - heading-medium · 24px · 32px · 500
  - heading-small · 20px · 28px · 500
  - heading-xsmall · 16px · 24px · 500
  - paragraph-large · 18px · 28px · 400
  - paragraph-medium · 16px · 24px · 400
  - paragraph-small · 14px · 20px · 400
  - paragraph-xsmall · 12px · 20px · 400
  - label-large · 16px · 20px · 500
  - label-medium · 14px · 16px · 500
  - label-small · 14px · 16px · 500
  - label-xsmall · 12px · 16px · 500
- **elevation**: emit section with `--shadow-1`, `--shadow-2`.

## Source

- https://baseweb.design
- Typography: https://baseweb.design/guides/typography/
- Foundation colors: https://baseweb.design/guides/theming/

UberMove is proprietary; stack falls back to system-ui.
