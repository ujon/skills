# Fluent Design System 2

Microsoft Fluent 2 — Segoe UI Variable, 50-step neutral ramp, Communication Blue brand, two-layer elevation shadows, and the Fluent motion ramp (ultra-fast → ultra-slow with Fluent easing curves). The modern design language used across Windows 11, Microsoft 365, and Fluent UI React v9.

## primitives/palette.css

```css
:root {
	/* Neutral — key steps from Fluent's 50-step grey ramp (grey-2 … grey-98) */
	--grey-2:   #050505;
	--grey-8:   #141414;
	--grey-10:  #1a1a1a;
	--grey-14:  #242424;
	--grey-22:  #383838;
	--grey-26:  #424242;
	--grey-38:  #616161;
	--grey-44:  #707070;
	--grey-58:  #949494;
	--grey-68:  #adadad;
	--grey-78:  #c7c7c7;
	--grey-80:  #cccccc;
	--grey-82:  #d1d1d1;
	--grey-88:  #e0e0e0;
	--grey-92:  #ebebeb;
	--grey-94:  #f0f0f0;
	--grey-96:  #f5f5f5;
	--grey-98:  #fafafa;
	--black:    #000000;
	--white:    #ffffff;

	/* Brand — Communication Blue (Fluent 2 default brand ramp) */
	--blue-shade50:  #001322;
	--blue-shade40:  #002440;
	--blue-shade30:  #004377;
	--blue-shade20:  #005ba1;
	--blue-shade10:  #006cbf;
	--blue-primary:  #0078d4;
	--blue-tint10:   #1a86d9;
	--blue-tint20:   #3595de;
	--blue-tint30:   #5caae5;
	--blue-tint40:   #a9d3f2;
	--blue-tint50:   #d0e7f8;
	--blue-tint60:   #f3f9fd;

	/* Status — Fluent palette reds/greens/yellows (shared palette) */
	--red-foreground:   #c50f1f;
	--red-background:   #fde7e9;
	--green-foreground: #0e700e;
	--green-background: #e2f3e1;
	--yellow-foreground:#bc4b09;
	--yellow-background:#fff4ce;
}
```

## primitives/size.css

```css
:root {
	/* Spacing — semantic subset, mapped to Fluent horizontal spacing */
	--space-xs: 4px;   /* spacingHorizontalXS */
	--space-sm: 8px;   /* spacingHorizontalS */
	--space-md: 12px;  /* spacingHorizontalM */
	--space-lg: 20px;  /* spacingHorizontalXL */
	--space-xl: 32px;  /* spacingHorizontalXXXL */

	/* Fluent full horizontal spacing ramp */
	--fluent-spacing-none:    0;
	--fluent-spacing-xxs:     2px;
	--fluent-spacing-xs:      4px;
	--fluent-spacing-s-nudge: 6px;
	--fluent-spacing-s:       8px;
	--fluent-spacing-m-nudge: 10px;
	--fluent-spacing-m:       12px;
	--fluent-spacing-l:       16px;
	--fluent-spacing-xl:      20px;
	--fluent-spacing-xxl:     24px;
	--fluent-spacing-xxxl:    32px;

	/* Button size — Fluent small / medium / large */
	--btn-sm: 24px;
	--btn-md: 32px;
	--btn-lg: 40px;

	/* Radius — semantic subset, mapped to Fluent corner scale */
	--radius-sm: 2px;  /* fluent-corner-small */
	--radius-md: 4px;  /* fluent-corner-medium — the Fluent default */
	--radius-lg: 8px;  /* fluent-corner-large */

	/* Fluent full corner scale */
	--fluent-corner-none:     0;
	--fluent-corner-small:    2px;
	--fluent-corner-medium:   4px;
	--fluent-corner-large:    8px;
	--fluent-corner-xlarge:   12px;
	--fluent-corner-circular: 9999px;

	/* Stroke widths (Fluent uses distinct stroke tokens for thicker borders) */
	--fluent-stroke-thin:    1px;
	--fluent-stroke-thick:   2px;
	--fluent-stroke-thicker: 3px;
	--fluent-stroke-thickest:4px;

	/* Transition — Fluent's "fast + easyEase" default */
	--transition: 150ms cubic-bezier(0.33, 0, 0.67, 1);
}
```

## primitives/typography.css

```css
:root {
	/* Font family — Segoe UI Variable on Windows, system fallback elsewhere */
	--font-sans: 'Segoe UI Variable', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif;
	--font-mono: 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'Menlo', 'Courier New', monospace;

	/* Font size — semantic steps mapped to Fluent ramp */
	--font-xs: 12px;  /* caption1 */
	--font-sm: 14px;  /* body1 */
	--font-md: 16px;  /* body2 */
	--font-lg: 20px;  /* subtitle1 */
	--font-xl: 28px;  /* title2 */
	--font-2xl: 40px; /* largeTitle */

	/* Fluent 2 type ramp — size / line-height / weight */
	--typography-caption2-size:        10px;
	--typography-caption2-line:        14px;
	--typography-caption2-weight:      400;
	--typography-caption1-size:        12px;
	--typography-caption1-line:        16px;
	--typography-caption1-weight:      400;
	--typography-caption1-strong-size: 12px;
	--typography-caption1-strong-line: 16px;
	--typography-caption1-strong-weight:700;
	--typography-body1-size:           14px;
	--typography-body1-line:           20px;
	--typography-body1-weight:         400;
	--typography-body1-strong-size:    14px;
	--typography-body1-strong-line:    20px;
	--typography-body1-strong-weight:  600;
	--typography-body2-size:           16px;
	--typography-body2-line:           22px;
	--typography-body2-weight:         400;
	--typography-body2-strong-size:    16px;
	--typography-body2-strong-line:    22px;
	--typography-body2-strong-weight:  600;
	--typography-subtitle2-size:       16px;
	--typography-subtitle2-line:       22px;
	--typography-subtitle2-weight:     600;
	--typography-subtitle1-size:       20px;
	--typography-subtitle1-line:       26px;
	--typography-subtitle1-weight:     600;
	--typography-title3-size:          24px;
	--typography-title3-line:          28px;
	--typography-title3-weight:        600;
	--typography-title2-size:          28px;
	--typography-title2-line:          36px;
	--typography-title2-weight:        600;
	--typography-title1-size:          32px;
	--typography-title1-line:          40px;
	--typography-title1-weight:        600;
	--typography-large-title-size:     40px;
	--typography-large-title-line:     52px;
	--typography-large-title-weight:   600;
	--typography-display-size:         68px;
	--typography-display-line:         92px;
	--typography-display-weight:       600;
}
```

## theme.css

```css
:root {
	color-scheme: light;

	/* Surfaces — Fluent webLightTheme colorNeutralBackground1..6 */
	--bg:          #ffffff;
	--bg-subtle:   #fafafa;
	--bg-muted:    #f5f5f5;
	--bg-elevated: #f0f0f0;

	/* Text — Fluent colorNeutralForeground1..3 */
	--fg:        #242424;
	--fg-muted:  #424242;
	--fg-subtle: #616161;

	/* Borders — Fluent colorNeutralStroke2 / Stroke1 */
	--border:        #e0e0e0;
	--border-strong: #d1d1d1;

	/* Brand — Communication Blue primary + tint container */
	--accent:        var(--blue-primary);
	--accent-muted:  var(--blue-tint50);
	--highlight:       var(--blue-primary);
	--highlight-muted: var(--blue-tint50);

	/* Status */
	--danger:  var(--red-foreground);
	--success: var(--green-foreground);
	--warning: var(--yellow-foreground);
}

[data-theme='dark'] {
	color-scheme: dark;

	/* Surfaces — Fluent webDarkTheme backgrounds */
	--bg:          #1f1f1f;  /* grey-12 */
	--bg-subtle:   #1a1a1a;  /* grey-10 */
	--bg-muted:    #141414;  /* grey-8 */
	--bg-elevated: #292929;  /* grey-16 */

	/* Text */
	--fg:        #ffffff;
	--fg-muted:  #d6d6d6;
	--fg-subtle: #adadad;

	/* Borders */
	--border:        #525252;
	--border-strong: #666666;

	/* Brand — use a lighter tint in dark mode for contrast */
	--accent:        var(--blue-tint20);
	--accent-muted:  color-mix(in srgb, var(--blue-tint20) 20%, transparent);
	--highlight:       var(--blue-tint20);
	--highlight-muted: color-mix(in srgb, var(--blue-tint20) 20%, transparent);

	/* Status — brighten in dark */
	--danger:  #f1707b;
	--success: #4ba54b;
	--warning: #f4b042;
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		color-scheme: dark;

		--bg:          #1f1f1f;
		--bg-subtle:   #1a1a1a;
		--bg-muted:    #141414;
		--bg-elevated: #292929;

		--fg:        #ffffff;
		--fg-muted:  #d6d6d6;
		--fg-subtle: #adadad;

		--border:        #525252;
		--border-strong: #666666;

		--accent:        var(--blue-tint20);
		--accent-muted:  color-mix(in srgb, var(--blue-tint20) 20%, transparent);
		--highlight:       var(--blue-tint20);
		--highlight-muted: color-mix(in srgb, var(--blue-tint20) 20%, transparent);

		--danger:  #f1707b;
		--success: #4ba54b;
		--warning: #f4b042;
	}
}
```

## primitives/motion.css

```css
:root {
	/* Fluent 2 motion durations */
	--fluent-duration-ultrafast: 50ms;
	--fluent-duration-faster:    100ms;
	--fluent-duration-fast:      150ms;
	--fluent-duration-normal:    200ms;
	--fluent-duration-slow:      300ms;
	--fluent-duration-slower:    400ms;
	--fluent-duration-ultraslow: 500ms;

	/* Fluent 2 easing curves */
	--fluent-curve-accelerate-max: cubic-bezier(0.9, 0.1, 1, 0.2);
	--fluent-curve-accelerate-mid: cubic-bezier(1, 0, 1, 1);
	--fluent-curve-accelerate-min: cubic-bezier(0.8, 0, 0.78, 1);
	--fluent-curve-decelerate-max: cubic-bezier(0.1, 0.9, 0.2, 1);
	--fluent-curve-decelerate-mid: cubic-bezier(0, 0, 0, 1);
	--fluent-curve-decelerate-min: cubic-bezier(0.33, 0, 0.1, 1);
	--fluent-curve-easy-ease:      cubic-bezier(0.33, 0, 0.67, 1);
	--fluent-curve-linear:         cubic-bezier(0, 0, 1, 1);
}
```

## primitives/effects.css

```css
:root {
	/* Fluent 2 elevation — two-layer shadows (ambient + key)
	   Light mode uses lower opacity; dark mode is overridden below. */
	--shadow-2:  0 0 2px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.14);
	--shadow-4:  0 0 2px rgba(0, 0, 0, 0.12), 0 2px 4px rgba(0, 0, 0, 0.14);
	--shadow-8:  0 0 2px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.14);
	--shadow-16: 0 0 2px rgba(0, 0, 0, 0.12), 0 8px 16px rgba(0, 0, 0, 0.14);
	--shadow-28: 0 0 8px rgba(0, 0, 0, 0.20), 0 14px 28px rgba(0, 0, 0, 0.24);
	--shadow-64: 0 0 8px rgba(0, 0, 0, 0.20), 0 32px 64px rgba(0, 0, 0, 0.24);
}

[data-theme='dark'] {
	/* Fluent 2 dark-mode shadows use higher opacity so shadows remain visible */
	--shadow-2:  0 0 2px rgba(0, 0, 0, 0.24), 0 1px 2px rgba(0, 0, 0, 0.28);
	--shadow-4:  0 0 2px rgba(0, 0, 0, 0.24), 0 2px 4px rgba(0, 0, 0, 0.28);
	--shadow-8:  0 0 2px rgba(0, 0, 0, 0.24), 0 4px 8px rgba(0, 0, 0, 0.28);
	--shadow-16: 0 0 2px rgba(0, 0, 0, 0.24), 0 8px 16px rgba(0, 0, 0, 0.28);
	--shadow-28: 0 0 8px rgba(0, 0, 0, 0.40), 0 14px 28px rgba(0, 0, 0, 0.48);
	--shadow-64: 0 0 8px rgba(0, 0, 0, 0.40), 0 32px 64px rgba(0, 0, 0, 0.48);
}

@media (prefers-color-scheme: dark) {
	[data-theme='system'] {
		--shadow-2:  0 0 2px rgba(0, 0, 0, 0.24), 0 1px 2px rgba(0, 0, 0, 0.28);
		--shadow-4:  0 0 2px rgba(0, 0, 0, 0.24), 0 2px 4px rgba(0, 0, 0, 0.28);
		--shadow-8:  0 0 2px rgba(0, 0, 0, 0.24), 0 4px 8px rgba(0, 0, 0, 0.28);
		--shadow-16: 0 0 2px rgba(0, 0, 0, 0.24), 0 8px 16px rgba(0, 0, 0, 0.28);
		--shadow-28: 0 0 8px rgba(0, 0, 0, 0.40), 0 14px 28px rgba(0, 0, 0, 0.48);
		--shadow-64: 0 0 8px rgba(0, 0, 0, 0.40), 0 32px 64px rgba(0, 0, 0, 0.48);
	}
}
```

## components/typography.css

```css
.caption2        { font-size: var(--typography-caption2-size);        line-height: var(--typography-caption2-line);        font-weight: var(--typography-caption2-weight); }
.caption1        { font-size: var(--typography-caption1-size);        line-height: var(--typography-caption1-line);        font-weight: var(--typography-caption1-weight); }
.caption1-strong { font-size: var(--typography-caption1-strong-size); line-height: var(--typography-caption1-strong-line); font-weight: var(--typography-caption1-strong-weight); }
.body1           { font-size: var(--typography-body1-size);           line-height: var(--typography-body1-line);           font-weight: var(--typography-body1-weight); }
.body1-strong    { font-size: var(--typography-body1-strong-size);    line-height: var(--typography-body1-strong-line);    font-weight: var(--typography-body1-strong-weight); }
.body2           { font-size: var(--typography-body2-size);           line-height: var(--typography-body2-line);           font-weight: var(--typography-body2-weight); }
.body2-strong    { font-size: var(--typography-body2-strong-size);    line-height: var(--typography-body2-strong-line);    font-weight: var(--typography-body2-strong-weight); }
.subtitle2       { font-size: var(--typography-subtitle2-size);       line-height: var(--typography-subtitle2-line);       font-weight: var(--typography-subtitle2-weight); }
.subtitle1       { font-size: var(--typography-subtitle1-size);       line-height: var(--typography-subtitle1-line);       font-weight: var(--typography-subtitle1-weight); }
.title3          { font-size: var(--typography-title3-size);          line-height: var(--typography-title3-line);          font-weight: var(--typography-title3-weight); }
.title2          { font-size: var(--typography-title2-size);          line-height: var(--typography-title2-line);          font-weight: var(--typography-title2-weight); }
.title1          { font-size: var(--typography-title1-size);          line-height: var(--typography-title1-line);          font-weight: var(--typography-title1-weight); }
.large-title     { font-size: var(--typography-large-title-size);     line-height: var(--typography-large-title-line);     font-weight: var(--typography-large-title-weight); }
.display         { font-size: var(--typography-display-size);         line-height: var(--typography-display-line);         font-weight: var(--typography-display-weight); }
```

## Preview metadata

- **name**: Fluent 2
- **description**: Microsoft Fluent 2 — Segoe UI Variable, Communication Blue, two-layer Fluent elevation, 14 type-ramp roles.
- **type_roles**: emit (size / line / weight):
  - caption2 · 10px · 14px · 400
  - caption1 · 12px · 16px · 400
  - caption1-strong · 12px · 16px · 700
  - body1 · 14px · 20px · 400
  - body1-strong · 14px · 20px · 600
  - body2 · 16px · 22px · 400
  - body2-strong · 16px · 22px · 600
  - subtitle2 · 16px · 22px · 600
  - subtitle1 · 20px · 26px · 600
  - title3 · 24px · 28px · 600
  - title2 · 28px · 36px · 600
  - title1 · 32px · 40px · 600
  - large-title · 40px · 52px · 600
  - display · 68px · 92px · 600
- **elevation**: emit section rendering `--shadow-2`, `--shadow-4`, `--shadow-8`, `--shadow-16`, `--shadow-28`, `--shadow-64` as live elevation boxes (via `{{EFFECTS_SECTION}}`).

## Source

- Fluent 2 design system overview: https://fluent2.microsoft.design/design-tokens
- Color ramp + brand palette: https://fluent2.microsoft.design/color
- Elevation shadows: https://fluent2.microsoft.design/elevation
- Corner scale (shapes): https://fluent2.microsoft.design/shapes
- Motion: https://fluent2.microsoft.design/motion
- Fluent UI React v9 token source: https://github.com/microsoft/fluentui/tree/master/packages/tokens
- Shadow values (two-layer): https://app.unpkg.com/@fluentui-react-native/design-tokens-windows@0.55.0

Segoe UI Variable is a Microsoft font; licensing restrictions apply on non-Microsoft platforms. System fallbacks (system-ui, -apple-system) cover non-Windows consumers gracefully. Motion curves and light-mode shadow opacities are in-house distillations calibrated against the Fluent 2 published spec.
