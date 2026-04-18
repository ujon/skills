# Radix Themes

Radix UI's design system (Radix Themes + Radix Colors). 12-step neutral (slate) + accent (blue), built for app chrome. Fits developer tools, dashboards, SaaS admin.

## primitives/palette.css

```css
:root {
	/* Slate 12-step — light */
	--slate-1: #FCFCFD;
	--slate-2: #F9F9FB;
	--slate-3: #EFF0F3;
	--slate-4: #E7E8EC;
	--slate-5: #E0E1E6;
	--slate-6: #D8D9DF;
	--slate-7: #CDCED7;
	--slate-8: #B9BBC6;
	--slate-9: #8B8D98;
	--slate-10: #80828D;
	--slate-11: #60646C;
	--slate-12: #1C2024;

	/* Slate 12-step — dark */
	--slate-dark-1: #111113;
	--slate-dark-2: #18191B;
	--slate-dark-3: #212225;
	--slate-dark-4: #272A2D;
	--slate-dark-5: #2E3135;
	--slate-dark-6: #363A3F;
	--slate-dark-7: #43484E;
	--slate-dark-8: #5A6169;
	--slate-dark-9: #696E77;
	--slate-dark-10: #777B84;
	--slate-dark-11: #B0B4BA;
	--slate-dark-12: #EDEEF0;

	/* Blue accent */
	--blue-1: #FBFDFF;
	--blue-2: #F4FAFF;
	--blue-3: #E6F4FE;
	--blue-4: #D5EFFF;
	--blue-5: #C2E5FF;
	--blue-6: #ACD8FC;
	--blue-7: #8EC8F6;
	--blue-8: #5EB1EF;
	--blue-9: #0090FF;
	--blue-10: #0588F0;
	--blue-11: #0D74CE;
	--blue-12: #113264;
	--blue-dark-4: #0A3069;
	--blue-dark-9: #0090FF;
	--blue-dark-10: #3B9EFF;
	--blue-dark-11: #70B8FF;

	/* Functional */
	--red-9: #E5484D;
	--red-10: #DC3E42;
	--green-9: #30A46C;
	--green-10: #2B9A66;
	--amber-9: #FFC53D;
	--amber-10: #FFBA18;
	--red-dark-9: #FF6369;
	--green-dark-9: #3DD68C;
}
```

## primitives/size.css

```css
:root {
	/* Spacing — Radix Themes spacing 1..7 */
	--space-xs: 4px;
	--space-sm: 8px;
	--space-md: 16px;
	--space-lg: 24px;
	--space-xl: 40px;

	/* Button size — Radix Themes button 2..4 */
	--btn-sm: 32px;
	--btn-md: 40px;
	--btn-lg: 48px;

	/* Radius — Radix Themes radius 2, 3, 5 */
	--radius-sm: 4px;
	--radius-md: 6px;
	--radius-lg: 12px;

	/* Transition */
	--transition: 140ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

## primitives/typography.css

```css
:root {
	/* Font family */
	--font-sans: 'Inter', 'SF Pro Text', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
	--font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Fira Code', monospace;

	/* Font size — mapped to Radix Themes text sizes */
	--font-xs: 12px;  /* text-1 */
	--font-sm: 14px;  /* text-2 */
	--font-md: 16px;  /* text-3 */
	--font-lg: 20px;  /* text-5 */
	--font-xl: 28px;  /* text-7 */
	--font-2xl: 35px; /* text-8 */
}
```

## theme.css

```css
:root {
	color-scheme: light;

	--bg: var(--slate-1);
	--bg-subtle: var(--slate-2);
	--bg-muted: var(--slate-3);
	--bg-elevated: var(--slate-4);

	--fg: var(--slate-12);
	--fg-muted: var(--slate-11);
	--fg-subtle: var(--slate-10);

	--border: var(--slate-6);
	--border-strong: var(--slate-8);

	--accent: var(--blue-9);
	--accent-muted: var(--blue-4);

	--highlight: var(--blue-10);
	--highlight-muted: var(--blue-3);

	--danger: var(--red-9);
	--success: var(--green-9);
	--warning: var(--amber-9);
}

[data-theme='dark'] {
	color-scheme: dark;

	--bg: var(--slate-dark-1);
	--bg-subtle: var(--slate-dark-2);
	--bg-muted: var(--slate-dark-3);
	--bg-elevated: var(--slate-dark-4);

	--fg: var(--slate-dark-12);
	--fg-muted: var(--slate-dark-11);
	--fg-subtle: var(--slate-dark-8);

	--border: var(--slate-dark-6);
	--border-strong: var(--slate-dark-7);

	--accent: var(--blue-dark-10);
	--accent-muted: var(--blue-dark-4);

	--highlight: var(--blue-dark-10);
	--highlight-muted: var(--blue-dark-4);

	--danger: var(--red-dark-9);
	--success: var(--green-dark-9);
	--warning: var(--amber-9);
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg: var(--slate-dark-1);
		--bg-subtle: var(--slate-dark-2);
		--bg-muted: var(--slate-dark-3);
		--bg-elevated: var(--slate-dark-4);

		--fg: var(--slate-dark-12);
		--fg-muted: var(--slate-dark-11);
		--fg-subtle: var(--slate-dark-8);

		--border: var(--slate-dark-6);
		--border-strong: var(--slate-dark-7);

		--accent: var(--blue-dark-10);
		--accent-muted: var(--blue-dark-4);

		--highlight: var(--blue-dark-10);
		--highlight-muted: var(--blue-dark-4);

		--danger: var(--red-dark-9);
		--success: var(--green-dark-9);
		--warning: var(--amber-9);
	}
}
```

## extras.css

```css
:root {
	/* Radix text roles */
	--typography-text-1-size: 12px;
	--typography-text-1-line: 16px;
	--typography-text-1-weight: 400;
	--typography-text-2-size: 14px;
	--typography-text-2-line: 20px;
	--typography-text-2-weight: 400;
	--typography-text-3-size: 16px;
	--typography-text-3-line: 24px;
	--typography-text-3-weight: 400;
	--typography-text-4-size: 18px;
	--typography-text-4-line: 26px;
	--typography-text-4-weight: 400;
	--typography-text-5-size: 20px;
	--typography-text-5-line: 28px;
	--typography-text-5-weight: 500;
	--typography-text-6-size: 24px;
	--typography-text-6-line: 30px;
	--typography-text-6-weight: 500;
	--typography-text-7-size: 28px;
	--typography-text-7-line: 36px;
	--typography-text-7-weight: 600;
	--typography-text-8-size: 35px;
	--typography-text-8-line: 40px;
	--typography-text-8-weight: 600;
	--typography-text-9-size: 60px;
	--typography-text-9-line: 60px;
	--typography-text-9-weight: 700;
}
```

## Preview metadata

- **name**: Radix Themes
- **description**: 12-step neutral + accent, developer UI, crisp radii.
- **type_roles**: emit:
  - text-1 · 12px · 16px · 400
  - text-2 · 14px · 20px · 400
  - text-3 · 16px · 24px · 400
  - text-4 · 18px · 26px · 400
  - text-5 · 20px · 28px · 500
  - text-6 · 24px · 30px · 500
  - text-7 · 28px · 36px · 600
  - text-8 · 35px · 40px · 600
  - text-9 · 60px · 60px · 700
- **elevation**: none — emit empty `{{ELEVATION_SECTION}}`.

## Source

- https://www.radix-ui.com/themes
- Colors: https://www.radix-ui.com/colors
- Typography: https://www.radix-ui.com/themes/docs/theme/typography
- Spacing: https://www.radix-ui.com/themes/docs/theme/spacing
- Radius: https://www.radix-ui.com/themes/docs/theme/radius

Radix Themes + Colors are MIT-licensed.
