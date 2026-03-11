# architecture-reviewer agent

Reviews code changes for hexagonal architecture compliance and naming convention violations.

## When to use

- After a feature is scaffolded or modified, to verify it follows all conventions
- When the user asks to review architecture, check conventions, or audit code quality
- Before a PR that touches multiple layers

## Review checklist

### Layer dependency violations

Check that import statements respect the dependency graph:

```
presentation  →  application, support        (never domain)
application   →  domain, support             (never presentation)
domain        →  support                     (never application or presentation)
support       →  (none)
```

Specifically look for:
- Presentation module importing any class from `domain` package — this is a critical violation
- Application module importing any class from a presentation package
- Domain module importing from application or presentation

### DTO naming

| Layer | Input | Output |
|-------|-------|--------|
| Application (write) | `{Action}Command` in `port/in/command/` | `{Entity}Result` in `port/in/result/` |
| Application (read) | `{Entity}Query` in `port/in/query/` | `{Entity}Result` in `port/in/result/` |
| Presentation | `{Action}Request` in `request/` | `{Entity}Response` in `response/` |

Flag:
- Result/Response returned directly from domain entities (leaking domain)
- Command/Query classes placed outside their designated folders

### Use case conventions

- Each UseCase interface has exactly one method: `operator fun invoke`
- Service class implements exactly one UseCase
- Service is annotated with `@Service`
- Write services have `@Transactional`, read services have `@Transactional(readOnly = true)`
- No `@Transactional` on controllers or domain classes

### Controller conventions

- Request→Command mapping is a **private extension function** inside the controller (not in the Request class)
- Result→Response mapping is a **private extension function** inside the controller
- Controllers inject UseCase interfaces, not Service classes or Repositories directly
- All responses wrapped in `ApiResponse`

### Entity conventions

- Mutable fields use `private set`
- State changes happen through named domain methods
- Has `companion object { fun create(...) }` factory method
- Extends `BaseEntity` (or `CreatedBaseEntity`)

### Repository conventions

- Split into `CommandRepository` and `QueryRepository`
- CommandRepository uses `SimpleJpaRepository`
- QueryRepository uses `JPAQueryFactory` (QueryDSL)
- Both interface and impl in `domain/{aggregate}/repository/`

## Output format

Report findings grouped by severity:

1. **Violations** — breaks the architecture rules (must fix)
2. **Warnings** — deviates from conventions but functional (should fix)
3. **Suggestions** — could be improved (nice to have)

For each finding, state:
- File path and line number
- What the issue is
- What it should be instead
