# Shopify Polaris

Shopify's commerce-oriented design system. Inter typeface, softly rounded corners, generous spacing, vivid brand accent. Fits e-commerce admin, marketplaces, and storefront-adjacent product UI.

## primitives/palette.css

```css
:root {
	--p-bg-0: #ffffff;
	--p-bg-100: #f7f7f7;
	--p-bg-200: #f1f1f1;
	--p-bg-300: #ebebeb;
	--p-bg-400: #dedede;

	--p-text: #303030;
	--p-text-secondary: #616161;
	--p-text-subtle: #8a8a8a;
	--p-text-disabled: #b5b5b5;
	--p-text-brand: #5521b5;

	--p-border: #e1e1e1;
	--p-border-strong: #c8c8c8;
	--p-border-focus: #005bd3;

	--p-brand-100: #d9e5ff;
	--p-brand-500: #005bd3;
	--p-brand-700: #00449e;

	--p-critical-500: #d72c0d;
	--p-success-500: #29845a;
	--p-warning-500: #916a00;

	--p-dark-bg: #1a1a1a;
	--p-dark-bg-subtle: #212121;
	--p-dark-bg-muted: #2a2a2a;
	--p-dark-bg-elevated: #303030;
	--p-dark-fg: #e3e3e3;
	--p-dark-fg-muted: #b5b5b5;
	--p-dark-fg-subtle: #8a8a8a;
	--p-dark-border: #3a3a3a;
	--p-dark-border-strong: #4a4a4a;
	--p-dark-accent: #3b82f6;
	--p-dark-accent-muted: #1e3a8a;
	--p-dark-danger: #ff6a5e;
	--p-dark-success: #52c785;
	--p-dark-warning: #ffc453;
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
	--btn-sm: 28px;
	--btn-md: 36px;
	--btn-lg: 44px;

	/* Radius */
	--radius-sm: 4px;
	--radius-md: 8px;
	--radius-lg: 12px;

	/* Transition */
	--transition: 150ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: 'Inter', 'SF Pro Text', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	--font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', monospace;

	/* Font size — mapped to Polaris roles */
	--font-xs: 12px;
	--font-sm: 14px;
	--font-md: 16px;
	--font-lg: 20px;
	--font-xl: 28px;
	--font-2xl: 40px;
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--p-bg-0);
	--bg-subtle: var(--p-bg-100);
	--bg-muted: var(--p-bg-200);
	--bg-elevated: var(--p-bg-300);

	--fg: var(--p-text);
	--fg-muted: var(--p-text-secondary);
	--fg-subtle: var(--p-text-subtle);

	--border: var(--p-border);
	--border-strong: var(--p-border-strong);

	--accent: var(--p-brand-500);
	--accent-muted: var(--p-brand-100);

	--highlight: var(--p-brand-500);
	--highlight-muted: var(--p-brand-100);

	--danger: var(--p-critical-500);
	--success: var(--p-success-500);
	--warning: var(--p-warning-500);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--p-dark-bg);
	--bg-subtle: var(--p-dark-bg-subtle);
	--bg-muted: var(--p-dark-bg-muted);
	--bg-elevated: var(--p-dark-bg-elevated);

	--fg: var(--p-dark-fg);
	--fg-muted: var(--p-dark-fg-muted);
	--fg-subtle: var(--p-dark-fg-subtle);

	--border: var(--p-dark-border);
	--border-strong: var(--p-dark-border-strong);

	--accent: var(--p-dark-accent);
	--accent-muted: var(--p-dark-accent-muted);

	--highlight: var(--p-dark-accent);
	--highlight-muted: var(--p-dark-accent-muted);

	--danger: var(--p-dark-danger);
	--success: var(--p-dark-success);
	--warning: var(--p-dark-warning);
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--p-dark-bg);
		--bg-subtle: var(--p-dark-bg-subtle);
		--bg-muted: var(--p-dark-bg-muted);
		--bg-elevated: var(--p-dark-bg-elevated);

		--fg: var(--p-dark-fg);
		--fg-muted: var(--p-dark-fg-muted);
		--fg-subtle: var(--p-dark-fg-subtle);

		--border: var(--p-dark-border);
		--border-strong: var(--p-dark-border-strong);

		--accent: var(--p-dark-accent);
		--accent-muted: var(--p-dark-accent-muted);

		--highlight: var(--p-dark-accent);
		--highlight-muted: var(--p-dark-accent-muted);

		--danger: var(--p-dark-danger);
		--success: var(--p-dark-success);
		--warning: var(--p-dark-warning);
	}
}
```

## extras.css

```css
:root {
	/* Polaris heading + body roles */
	--typography-heading-xs-size: 12px;
	--typography-heading-xs-line: 16px;
	--typography-heading-xs-weight: 650;
	--typography-heading-sm-size: 14px;
	--typography-heading-sm-line: 20px;
	--typography-heading-sm-weight: 650;
	--typography-heading-md-size: 16px;
	--typography-heading-md-line: 24px;
	--typography-heading-md-weight: 650;
	--typography-heading-lg-size: 20px;
	--typography-heading-lg-line: 28px;
	--typography-heading-lg-weight: 650;
	--typography-heading-xl-size: 24px;
	--typography-heading-xl-line: 28px;
	--typography-heading-xl-weight: 700;
	--typography-heading-2xl-size: 28px;
	--typography-heading-2xl-line: 32px;
	--typography-heading-2xl-weight: 700;
	--typography-heading-3xl-size: 32px;
	--typography-heading-3xl-line: 40px;
	--typography-heading-3xl-weight: 700;
	--typography-heading-4xl-size: 40px;
	--typography-heading-4xl-line: 48px;
	--typography-heading-4xl-weight: 700;

	--typography-body-xs-size: 12px;
	--typography-body-xs-line: 16px;
	--typography-body-xs-weight: 450;
	--typography-body-sm-size: 13px;
	--typography-body-sm-line: 20px;
	--typography-body-sm-weight: 450;
	--typography-body-md-size: 14px;
	--typography-body-md-line: 20px;
	--typography-body-md-weight: 450;
	--typography-body-lg-size: 16px;
	--typography-body-lg-line: 24px;
	--typography-body-lg-weight: 450;
}
```

## Preview metadata

- **name**: Shopify Polaris
- **description**: Inter, soft rounded, commerce-friendly. Generous spacing.
- **type_roles**: emit:
  - heading-xs · 12px · 16px · 650
  - heading-sm · 14px · 20px · 650
  - heading-md · 16px · 24px · 650
  - heading-lg · 20px · 28px · 650
  - heading-xl · 24px · 28px · 700
  - heading-2xl · 28px · 32px · 700
  - heading-3xl · 32px · 40px · 700
  - heading-4xl · 40px · 48px · 700
  - body-xs · 12px · 16px · 450
  - body-sm · 13px · 20px · 450
  - body-md · 14px · 20px · 450
  - body-lg · 16px · 24px · 450
- **elevation**: none — emit empty `{{ELEVATION_SECTION}}`.

## Source

- https://polaris.shopify.com
- Typography: https://polaris.shopify.com/tokens/font
- Color: https://polaris.shopify.com/tokens/color
- Space: https://polaris.shopify.com/tokens/space
- Shape: https://polaris.shopify.com/tokens/shape

Inter is SIL OFL; Polaris is MIT-licensed.
