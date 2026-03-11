# Commit Message Format Reference

This is the canonical commit message format. Use this as the source of truth when generating commit messages or IDE prompts.

## Structure

```
<title> (#<issue-number>)

## Summary
- Why the change was made
- What was changed (grouped by component)

## Changes
### <Group>
- `FileName` or `ClassName`:
  - Specific change details
```

## Title Rules

- Imperative mood, lowercase start after the verb, no period at the end
- Max 50 characters (excluding issue number)
- Start with a verb — no type prefixes like `feat:`, `fix:`
- Always append issue number: `(#123)` or `(#TBD)`

## Title Verb Patterns

| Verb       | When to Use                 |
|------------|-----------------------------|
| Add        | New feature or logic        |
| Improve    | Refactoring or optimization |
| Fix        | Bug fix                     |
| Change     | Behavior modification       |
| Remove     | Removing unused code        |
| Handle     | Exception/error handling    |
| Update     | Dependency or config update |

## Summary Rules

- 2-4 bullet points
- First bullet = **why** the change was made
- Remaining bullets = **what** was changed
- Note frameworks/libraries in parentheses when relevant

## Changes Section

- Group changes by the natural structure of the project
- Wrap code elements (file names, class names, function names) in backticks
- Each line under 72 characters

## How to Group Changes

Before writing the Changes section, look at the file paths in the diff to understand the project structure. The grouping should reflect how the project is actually organized, not a fixed template.

### Detecting project structure

1. Look at the changed file paths — the directory structure tells you the grouping style.
2. If the project has an established pattern (e.g., `src/domain/`, `src/api/`), follow it.
3. If the project has a flat structure or very few files, don't force grouping — just list the changes.

### Grouping styles

| Grouping Style | When to Use | Example Headers |
|----------------|-------------|-----------------|
| By layer | Layered or hexagonal architecture | `API`, `Domain`, `Infrastructure` |
| By module | Multi-module monorepo or package-based projects | `auth`, `payment`, `common` |
| By directory | Convention-based projects with meaningful directory names | `controllers/`, `models/`, `views/` |
| By concern | Cross-cutting changes or small projects | `Config`, `Build`, `Test`, `Docs` |
| Flat (no group) | Early-stage projects, few files, or single-concern changes | _(omit group headers entirely)_ |

Pick one style per commit and stay consistent within that message. When in doubt, mirror the directory structure.

### Early-stage projects

When the project has only a handful of files or no clear directory structure yet, skip the `### <Group>` headers and list changes directly under `## Changes`:

```
## Changes
- `SKILL.md`:
  - Add commit message generation workflow
- `commit-format.md`:
  - Add format rules and examples
```

This keeps the message clean without artificial grouping.

### Common Group Names

These are suggestions — derive group names from the actual project structure:

**Layered backend**:
API, Application, Domain, Infrastructure, Config, Schema

**Frontend**:
Components, Pages, Hooks, Store, Styles, Assets

**General**:
Build, Config, Test, Docs, Scripts, CI/CD

## Examples

### Simple Commit (title only)

For trivial changes (typo fix, single-line config change), skip Summary and Changes:

```
Fix typo in validation error message (#TBD)
```

### Early-Stage Project

When the project has few files and no clear structure:

```
Add commit message generation skill (#3)

## Summary
- Enable consistent commit message formatting across projects
- Add skill definition, format reference, and IDE variable docs

## Changes
- `SKILL.md`:
  - Add two-mode workflow (direct generation and IDE prompt)
- `references/commit-format.md`:
  - Add format rules, verb patterns, and grouping guidelines
- `references/ide-variables.md`:
  - Add template variables for 7 major IDEs
```

### Single-Layer Commit

```
Fix payment amount calculation error (#88)

## Summary
- Prevent incorrect totals when discount exceeds subtotal
- Clamp discount to subtotal before calculating final amount

## Changes
### Domain
- `PaymentCalculator`:
  - Add max-discount guard in `calculateTotal()`
```

### Multi-Layer Commit

```
Add refresh token flow and schema naming improvements (#142)

## Summary
- Add token refresh mechanism for seamless authentication
- Improve database schema naming for consistency

## Changes
### API
- `AuthController`:
  - Add `/auth/refresh` endpoint
  - Add request/response mapping extensions

### Application
- `RefreshTokenUseCase`:
  - Add use case interface with `Command` DTO
- `RefreshTokenService`:
  - Implement token validation and reissue logic

### Domain
- `TokenRepository`:
  - Add `findByRefreshToken` method

### Infrastructure
- `V2__rename_schema.sql`:
  - Rename table columns to follow naming convention
```

### Frontend Commit

```
Add product search with debounced input (#203)

## Summary
- Enable users to search products without excessive API calls
- Add debounced search input and result list component

## Changes
### Components
- `SearchInput`:
  - Add 300ms debounce on keystroke handler
- `ProductList`:
  - Add filtered rendering based on search query

### Hooks
- `useProductSearch`:
  - Add custom hook wrapping search API call
```

### Directory-Based Commit

```
Add user export to CSV with filtering (#77)

## Summary
- Allow admins to download filtered user lists as CSV
- Add export view, serializer, and CLI command

## Changes
### views/
- `UserExportView`:
  - Add GET handler with query param filtering

### serializers/
- `UserCSVSerializer`:
  - Add CSV row formatting for user model

### management/commands/
- `export_users.py`:
  - Add CLI command for scheduled exports
```

### Script Commit

```
Add benchmark aggregation script (#45)

## Summary
- Automate pass-rate and timing comparison across eval runs
- Generate markdown summary table from benchmark data

## Changes
### scripts/
- `aggregate_benchmark.py`:
  - Add JSON parsing and stats computation
  - Add markdown table generation
```

### Config / DevOps Commit

```
Add multi-stage Docker build and CI caching (#91)

## Summary
- Reduce container image size from 1.2GB to 340MB
- Speed up CI builds with layer caching

## Changes
### CI/CD
- `.github/workflows/build.yml`:
  - Add container layer cache action
  - Split build and push stages

### Config
- `Dockerfile`:
  - Rewrite as multi-stage build (builder + runtime)
- `docker-compose.yml`:
  - Add build cache volume mount
```

## Anti-Patterns

Avoid these in commit messages:

- Type prefixes: `feat:`, `fix:`, `refactor:` in the title
- Vague titles: "update", "fix stuff", "changes"
- Overly long or unfocused titles
- Excessive detail in bullet points
- Mixing unrelated changes in one message without clear grouping
