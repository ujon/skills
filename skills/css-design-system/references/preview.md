# Preview Template

Shared, system-agnostic pieces used to assemble files under `components/`, plus a single self-contained `styleguide.html`. Everything reads semantic tokens (`--fg`, `--bg`, `--space-md`, etc.) and works with any system without modification.

The preview is **one HTML file** — there is no separate `styleguide.css`. The full CSS bundle is inlined into a `<style>` block inside the HTML so the preview opens directly from the filesystem.

**Two class-name namespaces:**

- Plain names (`.btn`, `.input`, `.card`, `.alert`, …) — reusable component classes. They live in per-component files under `components/` and are safe to use in production. If they clash with an existing class, rename them with a global search-and-replace.
- `.sg-*` — preview-only chrome (page layout, swatches, type rows, theme toggle). Lives in the styleguide bundle only.

CSS uses **modern syntax** — native nesting (`&`), `:is()`, `color-mix()`, logical properties (`margin-inline`, `block-size`, `inset-block-end`). Supported in all current evergreen browsers.

**How to use this file**: each `## components/<name>.css` section below is written verbatim to that path. The `## components/index.css` section is the aggregator. Styleguide preview blocks (`## Reset`, `## Base`, `## Preview chrome CSS`, `## HTML template`, `## Components HTML`) are only used when the preview is enabled.

---

## components/index.css

```css
@import './button.css';
@import './form.css';
@import './badge.css';
@import './avatar.css';
@import './card.css';
@import './alert.css';
@import './progress.css';
@import './tabs.css';
@import './table.css';
@import './link.css';
```

---

## components/button.css

```css
.btn {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	gap: var(--space-xs);
	padding-inline: var(--space-md);
	block-size: var(--btn-md);
	border-radius: var(--radius-md);
	background: var(--bg-muted);
	color: var(--fg);
	font-size: var(--font-sm);
	font-weight: 500;
	border: 1px solid transparent;
	cursor: pointer;
	transition:
		background var(--transition),
		opacity var(--transition),
		border-color var(--transition);

	&:hover { background: var(--bg-elevated); }
	&:active { transform: translateY(1px); }

	&.primary {
		background: var(--accent);
		color: var(--bg);

		&:hover { opacity: 0.88; }
	}

	&.secondary {
		background: transparent;
		border-color: var(--border-strong);
		color: var(--fg);

		&:hover { background: var(--bg-subtle); }
	}

	&.ghost {
		background: transparent;
		color: var(--fg-muted);

		&:hover {
			background: var(--bg-subtle);
			color: var(--fg);
		}
	}

	&.danger {
		background: var(--danger);
		color: #fff;

		&:hover { opacity: 0.88; }
	}

	&.disabled,
	&:disabled {
		opacity: 0.45;
		pointer-events: none;
	}

	&.sm {
		block-size: var(--btn-sm);
		padding-inline: var(--space-sm);
		font-size: var(--font-xs);
	}

	&.lg {
		block-size: var(--btn-lg);
		padding-inline: var(--space-lg);
		font-size: var(--font-md);
	}
}
```

---

## components/form.css

Field wrapper, label, help text, input, textarea, select, checkbox/radio, and toggle switch. All read `--accent` so they inherit brand focus from the theme.

```css
.field {
	display: flex;
	flex-direction: column;
	gap: var(--space-xs);
}

.label {
	color: var(--fg-muted);
	font-size: var(--font-xs);
	font-weight: 500;
}

.help {
	color: var(--fg-subtle);
	font-size: var(--font-xs);

	&.error { color: var(--danger); }
}

:is(.input, .textarea, .select) {
	inline-size: 100%;
	padding-inline: var(--space-md);
	block-size: var(--btn-md);
	border: 1px solid var(--border);
	border-radius: var(--radius-md);
	background: var(--bg);
	color: var(--fg);
	font-size: var(--font-sm);
	transition:
		border-color var(--transition),
		box-shadow var(--transition);

	&::placeholder { color: var(--fg-subtle); }
	&:hover { border-color: var(--border-strong); }

	&:focus {
		outline: none;
		border-color: var(--accent);
		box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 20%, transparent);
	}

	&.error { border-color: var(--danger); }

	&:disabled {
		opacity: 0.5;
		pointer-events: none;
	}
}

.textarea {
	block-size: auto;
	min-block-size: calc(var(--btn-md) * 2.5);
	padding: var(--space-sm) var(--space-md);
	line-height: 1.5;
	resize: vertical;
}

.select {
	appearance: none;
	background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path d='M3 5 L6 8 L9 5' fill='none' stroke='%23808080' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/></svg>");
	background-repeat: no-repeat;
	background-position: right var(--space-md) center;
	padding-inline-end: calc(var(--space-md) * 2);
}

/* Checkbox & radio — native elements re-skinned via accent-color */
.choice {
	display: inline-flex;
	align-items: center;
	gap: var(--space-xs);
	font-size: var(--font-sm);
	color: var(--fg);
	cursor: pointer;

	& input:is([type='checkbox'], [type='radio']) {
		inline-size: 16px;
		block-size: 16px;
		accent-color: var(--accent);
		cursor: pointer;
	}

	&.disabled {
		opacity: 0.5;
		pointer-events: none;
	}
}

/* Toggle switch */
.switch {
	position: relative;
	display: inline-flex;
	inline-size: 36px;
	block-size: 20px;
	cursor: pointer;

	& input {
		appearance: none;
		position: absolute;
		inset: 0;
		margin: 0;
		opacity: 0;
		cursor: pointer;
	}

	& .switch-track {
		position: absolute;
		inset: 0;
		background: var(--border-strong);
		border-radius: 9999px;
		transition: background var(--transition);
	}

	& .switch-knob {
		position: absolute;
		inset-block-start: 2px;
		inset-inline-start: 2px;
		inline-size: 16px;
		block-size: 16px;
		background: var(--bg);
		border-radius: 50%;
		transition: transform var(--transition);
	}

	& input:checked ~ .switch-track { background: var(--accent); }
	& input:checked ~ .switch-knob { transform: translateX(16px); }
}
```

---

## components/badge.css

```css
.badge {
	display: inline-flex;
	align-items: center;
	gap: 4px;
	padding: 2px var(--space-sm);
	border-radius: 9999px;
	font-size: var(--font-xs);
	font-weight: 500;
	background: var(--bg-muted);
	color: var(--fg);
	border: 1px solid transparent;

	&.solid {
		background: var(--accent);
		color: var(--bg);
	}

	&.soft {
		background: color-mix(in srgb, var(--accent) 15%, transparent);
		color: var(--accent);
	}

	&.outline {
		background: transparent;
		border-color: var(--border-strong);
		color: var(--fg-muted);
	}

	&.danger {
		background: color-mix(in srgb, var(--danger) 15%, transparent);
		color: var(--danger);
	}

	&.success {
		background: color-mix(in srgb, var(--success) 15%, transparent);
		color: var(--success);
	}

	&.warning {
		background: color-mix(in srgb, var(--warning) 18%, transparent);
		color: var(--warning);
	}
}
```

---

## components/avatar.css

```css
.avatar {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	inline-size: 32px;
	block-size: 32px;
	border-radius: 50%;
	background: var(--bg-elevated);
	color: var(--fg-muted);
	font-size: var(--font-xs);
	font-weight: 600;
	border: 1px solid var(--border);

	&.lg {
		inline-size: 48px;
		block-size: 48px;
		font-size: var(--font-sm);
	}

	&.accent {
		background: var(--accent);
		color: var(--bg);
		border-color: transparent;
	}
}
```

---

## components/card.css

```css
.card {
	padding: var(--space-lg);
	background: var(--bg-subtle);
	border: 1px solid var(--border);
	border-radius: var(--radius-lg);

	& h4 {
		font-size: var(--font-md);
		margin-block-end: var(--space-xs);
	}

	& p {
		color: var(--fg-muted);
		font-size: var(--font-sm);
	}
}
```

---

## components/alert.css

```css
.alert {
	display: flex;
	align-items: flex-start;
	gap: var(--space-sm);
	padding: var(--space-sm) var(--space-md);
	border: 1px solid;
	border-radius: var(--radius-md);
	font-size: var(--font-sm);

	& .alert-icon {
		flex: none;
		inline-size: 18px;
		block-size: 18px;
		border-radius: 50%;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-size: 11px;
		font-weight: 700;
	}

	&.info {
		background: color-mix(in srgb, var(--highlight) 10%, transparent);
		color: var(--highlight);
		border-color: color-mix(in srgb, var(--highlight) 35%, transparent);

		& .alert-icon {
			background: var(--highlight);
			color: var(--bg);
		}
	}

	&.success {
		background: color-mix(in srgb, var(--success) 12%, transparent);
		color: var(--success);
		border-color: color-mix(in srgb, var(--success) 35%, transparent);

		& .alert-icon {
			background: var(--success);
			color: var(--bg);
		}
	}

	&.warning {
		background: color-mix(in srgb, var(--warning) 18%, transparent);
		color: var(--warning);
		border-color: color-mix(in srgb, var(--warning) 40%, transparent);

		& .alert-icon {
			background: var(--warning);
			color: var(--bg);
		}
	}

	&.danger {
		background: color-mix(in srgb, var(--danger) 12%, transparent);
		color: var(--danger);
		border-color: color-mix(in srgb, var(--danger) 35%, transparent);

		& .alert-icon {
			background: var(--danger);
			color: var(--bg);
		}
	}
}
```

---

## components/progress.css

```css
.progress {
	inline-size: 100%;
	block-size: 6px;
	background: var(--bg-muted);
	border-radius: 9999px;
	overflow: hidden;

	& .progress-fill {
		block-size: 100%;
		background: var(--accent);
		border-radius: 9999px;
		transition: inline-size var(--transition);
	}
}
```

---

## components/tabs.css

```css
.tabs {
	display: flex;
	gap: var(--space-md);
	border-block-end: 1px solid var(--border);

	& .tab {
		position: relative;
		padding-block: var(--space-sm);
		color: var(--fg-muted);
		font-size: var(--font-sm);
		font-weight: 500;
		border: none;
		background: none;
		cursor: pointer;

		&:hover { color: var(--fg); }

		&.active {
			color: var(--accent);

			&::after {
				content: '';
				position: absolute;
				inset-inline: 0;
				inset-block-end: -1px;
				block-size: 2px;
				background: var(--accent);
				border-radius: 2px 2px 0 0;
			}
		}
	}
}
```

---

## components/table.css

```css
.table {
	inline-size: 100%;
	font-size: var(--font-sm);
	border: 1px solid var(--border);
	border-radius: var(--radius-md);
	overflow: hidden;

	& :is(th, td) {
		padding: var(--space-sm) var(--space-md);
		text-align: start;
	}

	& thead {
		background: var(--bg-subtle);
		color: var(--fg-muted);
		font-weight: 500;
	}

	& tbody {
		& tr {
			border-block-start: 1px solid var(--border);

			&:hover { background: var(--bg-subtle); }
		}
	}
}
```

---

## components/link.css

```css
.link {
	color: var(--highlight);
	text-decoration: underline;
	text-underline-offset: 2px;

	&:hover { text-decoration-thickness: 2px; }
}
```

---

## Reset

Bundle-only block for the preview. Not written as a standalone file.

```css
/* ── Reset ── */
*,
*::before,
*::after {
	margin: 0;
	padding: 0;
	box-sizing: border-box;
}

a { color: inherit; text-decoration: none; }
button { border: none; background: none; cursor: pointer; font: inherit; color: inherit; }
input, textarea, select { border: none; background: none; font: inherit; color: inherit; }
ul, ol { list-style: none; }
img, svg { display: block; max-width: 100%; }
table { border-collapse: collapse; }
```

---

## Base

Element styles. Bundle-only.

```css
/* ── Base ── */
html,
body {
	min-block-size: 100%;
	background: var(--bg);
	color: var(--fg);
	font-family: var(--font-sans);
	font-size: var(--font-md);
	line-height: 1.5;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
}

:is(h1, h2, h3, h4) {
	font-weight: 600;
	line-height: 1.2;
}
h1 { font-size: var(--font-2xl); }
h2 { font-size: var(--font-xl); }
h3 { font-size: var(--font-lg); }

code {
	font-family: var(--font-mono);
	font-size: 0.92em;
	padding-inline: 4px;
	background: var(--bg-muted);
	border-radius: var(--radius-sm);
}

pre {
	font-family: var(--font-mono);
	font-size: var(--font-sm);
	background: var(--bg-subtle);
	border: 1px solid var(--border);
	border-radius: var(--radius-md);
	padding: var(--space-md);
	overflow-x: auto;

	& code {
		background: transparent;
		padding: 0;
	}
}

::selection { background: var(--fg); color: var(--bg); }
::-webkit-scrollbar { inline-size: 6px; block-size: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
	background: var(--border);
	border-radius: 3px;

	&:hover { background: var(--border-strong); }
}
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
```

---

## Preview chrome CSS

Preview-only layout and display widgets. Uses `.sg-*` prefix. Bundle-only.

```css
/* ── Preview layout ── */
.sg-root {
	max-inline-size: 1040px;
	margin-inline: auto;
	padding: var(--space-xl) var(--space-lg) calc(var(--space-xl) * 2);
}

.sg-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	gap: var(--space-md);
	padding-block-end: var(--space-lg);
	margin-block-end: var(--space-xl);
	border-block-end: 1px solid var(--border);

	& h1 {
		font-size: var(--font-xl);
		margin-block-end: var(--space-xs);
	}

	& .sg-sub {
		color: var(--fg-muted);
		font-size: var(--font-sm);
	}
}

.sg-section {
	margin-block-end: calc(var(--space-xl) * 1.25);

	& h2 {
		font-size: var(--font-lg);
		margin-block-end: var(--space-md);
		padding-block-end: var(--space-xs);
		border-block-end: 1px dashed var(--border);
	}

	& h3 {
		font-size: var(--font-md);
		color: var(--fg-muted);
		margin-block: var(--space-lg) var(--space-sm);
		font-weight: 500;
	}
}

/* Typography rows */
.sg-type-row {
	display: grid;
	grid-template-columns: 140px 1fr auto;
	gap: var(--space-md);
	padding-block: var(--space-sm);
	border-block-end: 1px solid var(--border);
	align-items: baseline;

	&:last-child { border-block-end: none; }

	& .sg-type-label {
		color: var(--fg-subtle);
		font-family: var(--font-mono);
		font-size: var(--font-xs);
	}

	& .sg-type-sample {
		color: var(--fg);
		line-height: 1.1;
	}

	& .sg-type-meta {
		color: var(--fg-muted);
		font-family: var(--font-mono);
		font-size: var(--font-xs);
		text-align: end;
		white-space: nowrap;
	}
}

/* Swatches */
.sg-swatch-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
	gap: var(--space-md);
}

.sg-swatch {
	border: 1px solid var(--border);
	border-radius: var(--radius-md);
	overflow: hidden;
	background: var(--bg);

	& .sg-swatch-preview {
		block-size: 64px;
		border-block-end: 1px solid var(--border);
	}

	& .sg-swatch-body {
		padding: var(--space-sm) var(--space-md);
		font-size: var(--font-xs);
	}

	& .sg-swatch-name {
		color: var(--fg);
		font-weight: 500;
	}

	& .sg-swatch-value {
		color: var(--fg-muted);
		font-family: var(--font-mono);
		margin-block-start: 2px;
	}
}

/* Spacing */
.sg-space-row {
	display: flex;
	align-items: center;
	gap: var(--space-md);
	padding-block: var(--space-xs);

	& .sg-space-label {
		min-inline-size: 90px;
		font-family: var(--font-mono);
		font-size: var(--font-xs);
		color: var(--fg-muted);
	}

	& .sg-space-bar {
		background: var(--accent);
		block-size: 16px;
		border-radius: var(--radius-sm);
	}

	& .sg-space-value {
		color: var(--fg-subtle);
		font-family: var(--font-mono);
		font-size: var(--font-xs);
	}
}

/* Radius */
.sg-radius-grid {
	display: grid;
	grid-template-columns: repeat(3, 1fr);
	gap: var(--space-md);
}

.sg-radius-box {
	aspect-ratio: 2 / 1;
	background: var(--bg-muted);
	border: 1px solid var(--border);
	display: flex;
	align-items: center;
	justify-content: center;
	font-family: var(--font-mono);
	font-size: var(--font-xs);
	color: var(--fg-muted);
}

/* Elevation */
.sg-elevation-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
	gap: var(--space-lg);
}

.sg-elevation-box {
	aspect-ratio: 3 / 2;
	background: var(--bg);
	border-radius: var(--radius-md);
	display: flex;
	align-items: center;
	justify-content: center;
	font-family: var(--font-mono);
	font-size: var(--font-xs);
	color: var(--fg-muted);
}

/* Layout helpers */
.sg-cluster {
	display: flex;
	gap: var(--space-sm);
	flex-wrap: wrap;
	align-items: center;
}

.sg-stack > * + * { margin-block-start: var(--space-md); }

.sg-grid-2 {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
	gap: var(--space-md);
}

/* Theme toggle */
.sg-toggle {
	font-family: var(--font-mono);
	font-size: var(--font-xs);
	padding-inline: var(--space-md);
	block-size: var(--btn-sm);
	border: 1px solid var(--border);
	border-radius: var(--radius-sm);
	color: var(--fg);
	background: var(--bg);
	cursor: pointer;
	transition: background var(--transition);

	&:hover { background: var(--bg-subtle); }
}
```

---

## HTML template

Substitute `{{...}}` placeholders per `SKILL.md` step 4. All placeholders are required; emit an empty string when there's nothing.

```html
<!doctype html>
<html lang="en" data-theme="light">
<head>
	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<title>Styleguide · {{SYSTEM_NAME}}</title>
	<style>
{{BUNDLED_CSS}}
	</style>
</head>
<body>
	<div class="sg-root">
		<header class="sg-header">
			<div>
				<h1>{{SYSTEM_NAME}}</h1>
				<div class="sg-sub">{{SYSTEM_DESCRIPTION}}</div>
			</div>
			<button class="sg-toggle" id="sg-theme-toggle">Theme: light</button>
		</header>

		<section class="sg-section">
			<h2>Typography</h2>
			{{TYPOGRAPHY_ROWS}}
		</section>

		<section class="sg-section">
			<h2>Palette</h2>
			<h3>Semantic roles</h3>
			<div class="sg-swatch-grid">{{SEMANTIC_SWATCHES}}</div>
			<h3>Primitive palette</h3>
			<div class="sg-swatch-grid">{{PRIMITIVE_SWATCHES}}</div>
		</section>

		<section class="sg-section">
			<h2>Spacing</h2>
			{{SPACING_ROWS}}
		</section>

		<section class="sg-section">
			<h2>Radius</h2>
			<div class="sg-radius-grid">{{RADIUS_BOXES}}</div>
		</section>

		{{ELEVATION_SECTION}}

		<section class="sg-section">
			<h2>Components</h2>
			{{COMPONENTS_BLOCK}}
		</section>
	</div>

	<script>
		const root = document.documentElement;
		const btn = document.getElementById('sg-theme-toggle');
		function paint_values() {
			const style = getComputedStyle(root);
			document.querySelectorAll('[data-var]').forEach(function (el) {
				const name = el.getAttribute('data-var');
				const v = style.getPropertyValue(name).trim();
				el.textContent = v || '—';
			});
		}
		btn.addEventListener('click', function () {
			const now = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
			root.setAttribute('data-theme', now);
			btn.textContent = 'Theme: ' + now;
			paint_values();
		});
		paint_values();
	</script>
</body>
</html>
```

---

## Placeholder patterns

### `{{TYPOGRAPHY_ROWS}}` — mutually exclusive

Emit exactly one of the two variants below, never both. Pick based on whether the system defines type roles in its reference file:

**Variant A — systems WITHOUT type roles** (Minimal, Polaris, Radix): emit six rows, one per `--font-xs` … `--font-2xl`.

```html
<div class="sg-type-row">
	<span class="sg-type-label">font-{KEY}</span>
	<span class="sg-type-sample" style="font-size: var(--font-{KEY});">The quick brown fox jumps</span>
	<span class="sg-type-meta" data-var="--font-{KEY}">—</span>
</div>
```

**Variant B — systems WITH type roles** (Material, Uber Base, Carbon, Maximal): emit one row per role. No `--font-*` scale rows, no extra `<h3>` heading.

```html
<div class="sg-type-row">
	<span class="sg-type-label">{ROLE_NAME}</span>
	<span class="sg-type-sample" style="font-size: {SIZE}; line-height: {LINE}; font-weight: {WEIGHT};">Design tokens styleguide</span>
	<span class="sg-type-meta">{SIZE} / {LINE} · {WEIGHT}</span>
</div>
```

### `{{SEMANTIC_SWATCHES}}`, `{{PRIMITIVE_SWATCHES}}`

```html
<div class="sg-swatch">
	<div class="sg-swatch-preview" style="background: var(--{NAME});"></div>
	<div class="sg-swatch-body">
		<div class="sg-swatch-name">{NAME}</div>
		<div class="sg-swatch-value" data-var="--{NAME}">—</div>
	</div>
</div>
```

### `{{SPACING_ROWS}}` — five rows

```html
<div class="sg-space-row">
	<span class="sg-space-label">space-{KEY}</span>
	<span class="sg-space-bar" style="inline-size: {VALUE};"></span>
	<span class="sg-space-value">{VALUE}</span>
</div>
```

### `{{RADIUS_BOXES}}` — three boxes

```html
<div class="sg-radius-box" style="border-radius: {VALUE};">radius-{KEY} · {VALUE}</div>
```

### `{{ELEVATION_SECTION}}` — optional

Empty string if no elevation. Otherwise:

```html
<section class="sg-section">
	<h2>Elevation</h2>
	<div class="sg-elevation-grid">{ELEVATION_BOXES}</div>
</section>
```

Each box:

```html
<div class="sg-elevation-box" style="box-shadow: {VALUE};">--{NAME}</div>
```

---

## Components HTML

Verbatim block for `{{COMPONENTS_BLOCK}}`. Uses the component selectors from `components/`.

```html
<h3>Buttons</h3>
<div class="sg-cluster">
	<button class="btn primary">Primary</button>
	<button class="btn secondary">Secondary</button>
	<button class="btn">Default</button>
	<button class="btn ghost">Ghost</button>
	<button class="btn danger">Danger</button>
	<button class="btn disabled">Disabled</button>
</div>
<div class="sg-cluster" style="margin-block-start: var(--space-sm);">
	<button class="btn primary sm">Small</button>
	<button class="btn primary">Medium</button>
	<button class="btn primary lg">Large</button>
</div>

<h3>Form</h3>
<div class="sg-grid-2">
	<div class="field">
		<label class="label" for="sg-email">Email</label>
		<input id="sg-email" class="input" placeholder="you@example.com" />
		<span class="help">We'll never share your address.</span>
	</div>
	<div class="field">
		<label class="label" for="sg-role">Role</label>
		<select id="sg-role" class="select">
			<option>Member</option>
			<option>Admin</option>
			<option>Owner</option>
		</select>
	</div>
	<div class="field" style="grid-column: 1 / -1;">
		<label class="label" for="sg-notes">Notes</label>
		<textarea id="sg-notes" class="textarea" placeholder="Write something…"></textarea>
	</div>
	<div class="field">
		<label class="label" for="sg-broken">Field with error</label>
		<input id="sg-broken" class="input error" value="invalid-email" />
		<span class="help error">Please enter a valid email.</span>
	</div>
	<div class="field">
		<label class="label">Preferences</label>
		<div class="sg-cluster">
			<label class="choice"><input type="checkbox" checked /> Newsletter</label>
			<label class="choice"><input type="checkbox" /> Product updates</label>
		</div>
		<div class="sg-cluster">
			<label class="choice"><input type="radio" name="plan" checked /> Monthly</label>
			<label class="choice"><input type="radio" name="plan" /> Yearly</label>
		</div>
		<label class="switch" aria-label="Enable notifications">
			<input type="checkbox" checked />
			<span class="switch-track"></span>
			<span class="switch-knob"></span>
		</label>
	</div>
</div>

<h3>Badges</h3>
<div class="sg-cluster">
	<span class="badge">Default</span>
	<span class="badge solid">Solid</span>
	<span class="badge soft">Soft</span>
	<span class="badge outline">Outline</span>
	<span class="badge danger">Danger</span>
	<span class="badge success">Success</span>
	<span class="badge warning">Warning</span>
</div>

<h3>Avatars</h3>
<div class="sg-cluster">
	<span class="avatar">JD</span>
	<span class="avatar accent">AK</span>
	<span class="avatar lg">MN</span>
</div>

<h3>Card</h3>
<div class="card">
	<h4>Card title</h4>
	<p>Cards sit on <code>--bg-subtle</code>, framed by <code>--border</code>, rounded by <code>--radius-lg</code>.</p>
</div>

<h3>Alerts</h3>
<div class="sg-stack">
	<div class="alert info"><span class="alert-icon">i</span><span>Tokens written to <code>styleguide-preview/</code>.</span></div>
	<div class="alert success"><span class="alert-icon">✓</span><span>All semantic roles resolved.</span></div>
	<div class="alert warning"><span class="alert-icon">!</span><span>Dark mode contrast is borderline on <code>--fg-subtle</code>.</span></div>
	<div class="alert danger"><span class="alert-icon">!</span><span>Missing semantic token <code>--highlight</code>.</span></div>
</div>

<h3>Progress</h3>
<div class="sg-stack" style="max-inline-size: 320px;">
	<div class="progress"><div class="progress-fill" style="inline-size: 28%;"></div></div>
	<div class="progress"><div class="progress-fill" style="inline-size: 62%;"></div></div>
	<div class="progress"><div class="progress-fill" style="inline-size: 94%;"></div></div>
</div>

<h3>Tabs</h3>
<div class="tabs">
	<button class="tab active">Overview</button>
	<button class="tab">Usage</button>
	<button class="tab">Tokens</button>
	<button class="tab">Accessibility</button>
</div>

<h3>Table</h3>
<table class="table">
	<thead>
		<tr><th>Token</th><th>Role</th><th>Light</th><th>Dark</th></tr>
	</thead>
	<tbody>
		<tr><td><code>--bg</code></td><td>App background</td><td>var(--bg)</td><td>var(--bg)</td></tr>
		<tr><td><code>--fg</code></td><td>Body text</td><td>var(--fg)</td><td>var(--fg)</td></tr>
		<tr><td><code>--accent</code></td><td>Primary action</td><td>var(--accent)</td><td>var(--accent)</td></tr>
		<tr><td><code>--border</code></td><td>Default border</td><td>var(--border)</td><td>var(--border)</td></tr>
	</tbody>
</table>

<h3>Links and inline</h3>
<p>Read the <a class="link" href="#">design-systems reference</a> for selection heuristics. Inline <code>code</code> uses <code>--bg-muted</code>.</p>

<h3>Code block</h3>
<pre><code>const tokens = {
  bg: 'var(--bg)',
  fg: 'var(--fg)',
  space: 'var(--space-md)',
  radius: 'var(--radius-md)',
};
</code></pre>
```
