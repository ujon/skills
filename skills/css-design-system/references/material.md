# Material Design 3

Google's Material 3. Recognizable, heavily specified, a solid pick when the user wants a consumer-facing system with strong defaults.

## primitives/palette.css

```css
:root {
	/* primary (purple) */
	--primary-10: #21005D;
	--primary-20: #381E72;
	--primary-30: #4F378B;
	--primary-40: #6750A4;
	--primary-80: #D0BCFF;
	--primary-90: #EADDFF;
	--primary-99: #FFFBFE;

	/* secondary */
	--secondary-10: #1D192B;
	--secondary-30: #4A4458;
	--secondary-40: #625B71;
	--secondary-90: #E8DEF8;

	/* tertiary */
	--tertiary-40: #7D5260;
	--tertiary-90: #FFD8E4;

	/* neutral */
	--neutral-10: #1C1B1F;
	--neutral-20: #313033;
	--neutral-30: #484649;
	--neutral-40: #605D62;
	--neutral-50: #787579;
	--neutral-60: #939094;
	--neutral-70: #AEAAAE;
	--neutral-80: #C9C5CA;
	--neutral-90: #E6E1E5;
	--neutral-95: #F4EFF4;
	--neutral-99: #FFFBFE;

	/* neutral-variant */
	--neutral-variant-30: #49454F;
	--neutral-variant-50: #79747E;
	--neutral-variant-60: #938F99;
	--neutral-variant-80: #CAC4D0;
	--neutral-variant-90: #E7E0EC;

	/* error */
	--error-10: #410E0B;
	--error-40: #B3261E;
	--error-80: #F2B8B5;
	--error-90: #F9DEDC;
}
```

## primitives/size.css

```css
:root {
	/* Spacing — MD3 4dp grid */
	--space-xs: 4px;
	--space-sm: 8px;
	--space-md: 16px;
	--space-lg: 24px;
	--space-xl: 40px;

	/* Button size */
	--btn-sm: 32px;
	--btn-md: 40px;
	--btn-lg: 48px;

	/* Radius — MD3 shape scale (semantic subset) */
	--radius-sm: 8px;
	--radius-md: 12px;
	--radius-lg: 16px;

	/* MD3 full shape scale */
	--md-shape-none: 0;
	--md-shape-xs: 4px;
	--md-shape-sm: 8px;
	--md-shape-md: 12px;
	--md-shape-lg: 16px;
	--md-shape-xl: 28px;
	--md-shape-full: 9999px;

	/* Transition */
	--transition: 200ms cubic-bezier(0.2, 0, 0, 1);
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: 'Roboto', 'Noto Sans', system-ui, sans-serif;
	--font-mono: 'Roboto Mono', 'Courier New', monospace;

	/* Font size — six semantic steps, mapped to MD3 roles */
	--font-xs: 12px;  /* ≈ body-small */
	--font-sm: 14px;  /* ≈ body-medium / label-large */
	--font-md: 16px;  /* ≈ body-large */
	--font-lg: 22px;  /* ≈ title-large */
	--font-xl: 28px;  /* ≈ headline-medium */
	--font-2xl: 36px; /* ≈ display-small */

	/* MD3 full type roles */
	--typography-display-large-size: 57px;
	--typography-display-large-line: 64px;
	--typography-display-large-weight: 400;
	--typography-display-medium-size: 45px;
	--typography-display-medium-line: 52px;
	--typography-display-medium-weight: 400;
	--typography-display-small-size: 36px;
	--typography-display-small-line: 44px;
	--typography-display-small-weight: 400;
	--typography-headline-large-size: 32px;
	--typography-headline-large-line: 40px;
	--typography-headline-large-weight: 400;
	--typography-headline-medium-size: 28px;
	--typography-headline-medium-line: 36px;
	--typography-headline-medium-weight: 400;
	--typography-headline-small-size: 24px;
	--typography-headline-small-line: 32px;
	--typography-headline-small-weight: 400;
	--typography-title-large-size: 22px;
	--typography-title-large-line: 28px;
	--typography-title-large-weight: 400;
	--typography-title-medium-size: 16px;
	--typography-title-medium-line: 24px;
	--typography-title-medium-weight: 500;
	--typography-title-small-size: 14px;
	--typography-title-small-line: 20px;
	--typography-title-small-weight: 500;
	--typography-body-large-size: 16px;
	--typography-body-large-line: 24px;
	--typography-body-large-weight: 400;
	--typography-body-medium-size: 14px;
	--typography-body-medium-line: 20px;
	--typography-body-medium-weight: 400;
	--typography-body-small-size: 12px;
	--typography-body-small-line: 16px;
	--typography-body-small-weight: 400;
	--typography-label-large-size: 14px;
	--typography-label-large-line: 20px;
	--typography-label-large-weight: 500;
	--typography-label-medium-size: 12px;
	--typography-label-medium-line: 16px;
	--typography-label-medium-weight: 500;
	--typography-label-small-size: 11px;
	--typography-label-small-line: 16px;
	--typography-label-small-weight: 500;
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--neutral-99);
	--bg-subtle: var(--neutral-95);
	--bg-muted: var(--neutral-90);
	--bg-elevated: var(--neutral-variant-90);

	--fg: var(--neutral-10);
	--fg-muted: var(--neutral-variant-30);
	--fg-subtle: var(--neutral-50);

	--border: var(--neutral-variant-80);
	--border-strong: var(--neutral-variant-60);

	--accent: var(--primary-40);
	--accent-muted: var(--primary-80);

	--highlight: var(--primary-40);
	--highlight-muted: var(--primary-90);

	--danger: var(--error-40);
	--success: #146C2E;
	--warning: #825500;
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--neutral-10);
	--bg-subtle: #141218;
	--bg-muted: var(--neutral-20);
	--bg-elevated: var(--neutral-30);

	--fg: var(--neutral-90);
	--fg-muted: var(--neutral-variant-80);
	--fg-subtle: var(--neutral-60);

	--border: var(--neutral-variant-30);
	--border-strong: var(--neutral-variant-50);

	--accent: var(--primary-80);
	--accent-muted: var(--primary-30);

	--highlight: var(--primary-80);
	--highlight-muted: var(--primary-20);

	--danger: var(--error-80);
	--success: #6DD48E;
	--warning: #FFB95C;
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--neutral-10);
		--bg-subtle: #141218;
		--bg-muted: var(--neutral-20);
		--bg-elevated: var(--neutral-30);

		--fg: var(--neutral-90);
		--fg-muted: var(--neutral-variant-80);
		--fg-subtle: var(--neutral-60);

		--border: var(--neutral-variant-30);
		--border-strong: var(--neutral-variant-50);

		--accent: var(--primary-80);
		--accent-muted: var(--primary-30);

		--highlight: var(--primary-80);
		--highlight-muted: var(--primary-20);

		--danger: var(--error-80);
		--success: #6DD48E;
		--warning: #FFB95C;
	}
}
```

## primitives/motion.css

```css
:root {
	/* MD3 motion */
	--md-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
	--md-motion-easing-emphasized: cubic-bezier(0.3, 0, 0, 1);
	--md-motion-duration-short: 200ms;
	--md-motion-duration-medium: 400ms;
	--md-motion-duration-long: 600ms;
}
```

## primitives/effects.css

```css
:root {
	/* MD3 elevation */
	--elevation-0: none;
	--elevation-1: 0 1px 2px rgba(0, 0, 0, 0.3), 0 1px 3px 1px rgba(0, 0, 0, 0.15);
	--elevation-2: 0 1px 2px rgba(0, 0, 0, 0.3), 0 2px 6px 2px rgba(0, 0, 0, 0.15);
	--elevation-3: 0 4px 8px 3px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.3);
	--elevation-4: 0 6px 10px 4px rgba(0, 0, 0, 0.15), 0 2px 3px rgba(0, 0, 0, 0.3);
	--elevation-5: 0 8px 12px 6px rgba(0, 0, 0, 0.15), 0 4px 4px rgba(0, 0, 0, 0.3);
}
```

## components/typography.css

```css
.display-large   { font-size: var(--typography-display-large-size);   line-height: var(--typography-display-large-line);   font-weight: var(--typography-display-large-weight); }
.display-medium  { font-size: var(--typography-display-medium-size);  line-height: var(--typography-display-medium-line);  font-weight: var(--typography-display-medium-weight); }
.display-small   { font-size: var(--typography-display-small-size);   line-height: var(--typography-display-small-line);   font-weight: var(--typography-display-small-weight); }
.headline-large  { font-size: var(--typography-headline-large-size);  line-height: var(--typography-headline-large-line);  font-weight: var(--typography-headline-large-weight); }
.headline-medium { font-size: var(--typography-headline-medium-size); line-height: var(--typography-headline-medium-line); font-weight: var(--typography-headline-medium-weight); }
.headline-small  { font-size: var(--typography-headline-small-size);  line-height: var(--typography-headline-small-line);  font-weight: var(--typography-headline-small-weight); }
.title-large     { font-size: var(--typography-title-large-size);     line-height: var(--typography-title-large-line);     font-weight: var(--typography-title-large-weight); }
.title-medium    { font-size: var(--typography-title-medium-size);    line-height: var(--typography-title-medium-line);    font-weight: var(--typography-title-medium-weight); }
.title-small     { font-size: var(--typography-title-small-size);     line-height: var(--typography-title-small-line);     font-weight: var(--typography-title-small-weight); }
.body-large      { font-size: var(--typography-body-large-size);      line-height: var(--typography-body-large-line);      font-weight: var(--typography-body-large-weight); }
.body-medium     { font-size: var(--typography-body-medium-size);     line-height: var(--typography-body-medium-line);     font-weight: var(--typography-body-medium-weight); }
.body-small      { font-size: var(--typography-body-small-size);      line-height: var(--typography-body-small-line);      font-weight: var(--typography-body-small-weight); }
.label-large     { font-size: var(--typography-label-large-size);     line-height: var(--typography-label-large-line);     font-weight: var(--typography-label-large-weight); }
.label-medium    { font-size: var(--typography-label-medium-size);    line-height: var(--typography-label-medium-line);    font-weight: var(--typography-label-medium-weight); }
.label-small     { font-size: var(--typography-label-small-size);     line-height: var(--typography-label-small-line);     font-weight: var(--typography-label-small-weight); }
```

## Preview metadata

- **name**: Material Design 3
- **description**: Google MD3 — Roboto, tonal palette, shape + elevation scale.
- **type_roles**: emit these rows (name / size / line / weight):
  - display-large · 57px · 64px · 400
  - display-medium · 45px · 52px · 400
  - display-small · 36px · 44px · 400
  - headline-large · 32px · 40px · 400
  - headline-medium · 28px · 36px · 400
  - headline-small · 24px · 32px · 400
  - title-large · 22px · 28px · 400
  - title-medium · 16px · 24px · 500
  - title-small · 14px · 20px · 500
  - body-large · 16px · 24px · 400
  - body-medium · 14px · 20px · 400
  - body-small · 12px · 16px · 400
  - label-large · 14px · 20px · 500
  - label-medium · 12px · 16px · 500
  - label-small · 11px · 16px · 500
- **elevation**: emit section with boxes for `--elevation-0` through `--elevation-5`.

## Source

- https://m3.material.io
- Type: https://m3.material.io/styles/typography/type-scale-tokens
- Color roles: https://m3.material.io/styles/color/roles
- Shape: https://m3.material.io/styles/shape/shape-scale-tokens
- Elevation: https://m3.material.io/styles/elevation/tokens

Spec: MD3 (2024). Verify upstream if exact fidelity matters.
