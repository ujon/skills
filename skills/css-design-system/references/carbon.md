# IBM Carbon

IBM's enterprise design system. IBM Plex Sans, sharp radii, 16-step neutral gray, high-contrast. Fits data-heavy enterprise UI and accessibility-sensitive work.

## primitives/palette.css

```css
:root {
	--white: #ffffff;
	--black: #000000;

	--gray-10: #f4f4f4;
	--gray-20: #e0e0e0;
	--gray-30: #c6c6c6;
	--gray-40: #a8a8a8;
	--gray-50: #8d8d8d;
	--gray-60: #6f6f6f;
	--gray-70: #525252;
	--gray-80: #393939;
	--gray-90: #262626;
	--gray-100: #161616;

	--blue-40: #4589ff;
	--blue-60: #0f62fe;
	--blue-70: #0043ce;
	--blue-80: #002d9c;

	--red-50: #fa4d56;
	--red-60: #da1e28;
	--red-70: #a2191f;

	--green-40: #42be65;
	--green-50: #24a148;

	--yellow-30: #f1c21b;
	--purple-60: #8a3ffc;
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

	/* Radius — Carbon is famously sharp */
	--radius-sm: 0;
	--radius-md: 2px;
	--radius-lg: 4px;

	/* Transition — Carbon productive motion */
	--transition: 110ms cubic-bezier(0, 0, 0.38, 0.9);
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
	--font-mono: 'IBM Plex Mono', 'Menlo', 'DejaVu Sans Mono', monospace;

	/* Font size — mapped to Carbon productive scale */
	--font-xs: 12px;  /* label-01 / helper-text-01 */
	--font-sm: 14px;  /* body-01 / heading-01 */
	--font-md: 16px;  /* body-02 / heading-02 */
	--font-lg: 20px;  /* heading-03 */
	--font-xl: 28px;  /* heading-04 */
	--font-2xl: 32px; /* heading-05 */
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--white);
	--bg-subtle: var(--gray-10);
	--bg-muted: var(--gray-20);
	--bg-elevated: var(--gray-30);

	--fg: var(--gray-100);
	--fg-muted: var(--gray-70);
	--fg-subtle: var(--gray-60);

	--border: var(--gray-30);
	--border-strong: var(--gray-50);

	--accent: var(--blue-60);
	--accent-muted: var(--blue-70);

	--highlight: var(--blue-60);
	--highlight-muted: #d0e2ff;

	--danger: var(--red-60);
	--success: var(--green-50);
	--warning: var(--yellow-30);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--gray-100);
	--bg-subtle: var(--gray-90);
	--bg-muted: var(--gray-80);
	--bg-elevated: var(--gray-70);

	--fg: var(--white);
	--fg-muted: var(--gray-30);
	--fg-subtle: var(--gray-40);

	--border: var(--gray-80);
	--border-strong: var(--gray-60);

	--accent: var(--blue-40);
	--accent-muted: var(--blue-70);

	--highlight: var(--blue-40);
	--highlight-muted: var(--blue-80);

	--danger: var(--red-50);
	--success: var(--green-40);
	--warning: var(--yellow-30);
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--gray-100);
		--bg-subtle: var(--gray-90);
		--bg-muted: var(--gray-80);
		--bg-elevated: var(--gray-70);

		--fg: var(--white);
		--fg-muted: var(--gray-30);
		--fg-subtle: var(--gray-40);

		--border: var(--gray-80);
		--border-strong: var(--gray-60);

		--accent: var(--blue-40);
		--accent-muted: var(--blue-70);

		--highlight: var(--blue-40);
		--highlight-muted: var(--blue-80);

		--danger: var(--red-50);
		--success: var(--green-40);
		--warning: var(--yellow-30);
	}
}
```

## extras.css

```css
:root {
	/* Carbon productive type roles */
	--typography-caption-01-size: 12px;
	--typography-caption-01-line: 16px;
	--typography-caption-01-weight: 400;
	--typography-label-01-size: 12px;
	--typography-label-01-line: 16px;
	--typography-label-01-weight: 400;
	--typography-helper-text-01-size: 12px;
	--typography-helper-text-01-line: 16px;
	--typography-helper-text-01-weight: 400;
	--typography-body-01-size: 14px;
	--typography-body-01-line: 20px;
	--typography-body-01-weight: 400;
	--typography-body-02-size: 16px;
	--typography-body-02-line: 24px;
	--typography-body-02-weight: 400;
	--typography-heading-01-size: 14px;
	--typography-heading-01-line: 18px;
	--typography-heading-01-weight: 600;
	--typography-heading-02-size: 16px;
	--typography-heading-02-line: 22px;
	--typography-heading-02-weight: 600;
	--typography-heading-03-size: 20px;
	--typography-heading-03-line: 28px;
	--typography-heading-03-weight: 400;
	--typography-heading-04-size: 28px;
	--typography-heading-04-line: 36px;
	--typography-heading-04-weight: 400;
	--typography-heading-05-size: 32px;
	--typography-heading-05-line: 40px;
	--typography-heading-05-weight: 400;
	--typography-heading-06-size: 42px;
	--typography-heading-06-line: 50px;
	--typography-heading-06-weight: 300;
	--typography-heading-07-size: 54px;
	--typography-heading-07-line: 64px;
	--typography-heading-07-weight: 300;
}
```

## Preview metadata

- **name**: IBM Carbon
- **description**: IBM Plex Sans, sharp radii, 16-step gray, high-contrast enterprise.
- **type_roles**: emit:
  - caption-01 · 12px · 16px · 400
  - label-01 · 12px · 16px · 400
  - body-01 · 14px · 20px · 400
  - body-02 · 16px · 24px · 400
  - heading-01 · 14px · 18px · 600
  - heading-02 · 16px · 22px · 600
  - heading-03 · 20px · 28px · 400
  - heading-04 · 28px · 36px · 400
  - heading-05 · 32px · 40px · 400
  - heading-06 · 42px · 50px · 300
  - heading-07 · 54px · 64px · 300
- **elevation**: none — emit empty `{{ELEVATION_SECTION}}`.

## Source

- https://carbondesignsystem.com
- Type: https://carbondesignsystem.com/guidelines/typography/overview
- Color tokens: https://carbondesignsystem.com/elements/color/tokens
- Spacing: https://carbondesignsystem.com/guidelines/spacing/overview

Spec: Carbon v11. IBM Plex is SIL OFL; safe to self-host.
