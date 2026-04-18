# Minimal

Monochrome + accents, system-font stack. The simplest system — a tidy set of CSS variables without adopting a named design system.

## primitives/palette.css

```css
:root {
	--black: #000;
	--gray-950: #111;
	--gray-900: #1a1a1a;
	--gray-800: #222;
	--gray-700: #333;
	--gray-600: #555;
	--gray-500: #666;
	--gray-400: #999;
	--gray-300: #ccc;
	--gray-200: #e0e0e0;
	--gray-100: #eee;
	--gray-50: #f5f5f5;
	--white: #fff;

	--red: #ff4444;
	--green: #34a853;
	--yellow: #ffaa00;
	--blue: #4a90d9;
	--purple: #a855f7;
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
	--btn-md: 32px;
	--btn-lg: 40px;

	/* Radius */
	--radius-sm: 4px;
	--radius-md: 8px;
	--radius-lg: 12px;

	/* Transition */
	--transition: 150ms ease;
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
	--font-mono: 'SF Mono', 'Fira Code', 'Consolas', monospace;

	/* Font size — six semantic steps */
	--font-xs: 11px;
	--font-sm: 13px;
	--font-md: 15px;
	--font-lg: 18px;
	--font-xl: 24px;
	--font-2xl: 32px;
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--white);
	--bg-subtle: var(--gray-50);
	--bg-muted: var(--gray-100);
	--bg-elevated: var(--gray-200);

	--fg: var(--black);
	--fg-muted: var(--gray-600);
	--fg-subtle: var(--gray-500);

	--border: var(--gray-300);
	--border-strong: var(--gray-400);

	--accent: var(--black);
	--accent-muted: var(--gray-600);

	--highlight: #2563eb;
	--highlight-muted: #93c5fd;

	--danger: var(--red);
	--success: var(--green);
	--warning: var(--yellow);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--black);
	--bg-subtle: var(--gray-950);
	--bg-muted: var(--gray-900);
	--bg-elevated: var(--gray-800);

	--fg: var(--white);
	--fg-muted: var(--gray-400);
	--fg-subtle: var(--gray-500);

	--border: var(--gray-700);
	--border-strong: var(--gray-600);

	--accent: var(--white);
	--accent-muted: var(--gray-300);

	--highlight: #60a5fa;
	--highlight-muted: #3b82f6;
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--black);
		--bg-subtle: var(--gray-950);
		--bg-muted: var(--gray-900);
		--bg-elevated: var(--gray-800);

		--fg: var(--white);
		--fg-muted: var(--gray-400);
		--fg-subtle: var(--gray-500);

		--border: var(--gray-700);
		--border-strong: var(--gray-600);

		--accent: var(--white);
		--accent-muted: var(--gray-300);

		--highlight: #60a5fa;
		--highlight-muted: #3b82f6;
	}
}
```

## extras.css

None. Minimal has no system-specific tokens beyond the invariants.

## Preview metadata

- **name**: Minimal
- **description**: Monochrome + accents, system font. Clean baseline.
- **type_roles**: none — emit empty `{{TYPE_ROLES_BLOCK}}`
- **elevation**: none — emit empty `{{ELEVATION_SECTION}}`

## Source

In-house. No external spec; tune values freely.
