# feature-scaffold agent

Scaffolds a complete vertical slice for a new feature across all hexagonal architecture layers.

## When to use

When the user asks to add a new feature, create a new use case, add an endpoint, or scaffold code that spans multiple layers.

## Before you start

1. Identify the project's **base package** by reading an existing source file (e.g., any entity or service)
2. Identify which **presentation module(s)** exist (look for `*-api`, `*-admin`, etc. in `settings.gradle.kts`)
3. Read a similar existing feature for reference — pick the feature closest to what's being requested and study its files across all layers

## Input required from user

- **Feature name**: the aggregate/domain concept (e.g., "bookmark", "notification")
- **Operations**: which use cases (e.g., create, list, detail, update, delete, toggle)
- **Target presentation module**: which module gets the controller
- **Entity fields**: what data the entity holds (if a new entity is needed)

If the user hasn't specified all of these, ask before proceeding.

## Generation order

Generate files strictly bottom-up. Each step depends on the previous:

### 1. Support layer (if needed)

Only create these if the feature introduces cross-layer types:

- `support/.../type/{Status}.kt` — status enum (e.g., `BookmarkStatus`)
- New `ErrorCode` entry — only if no existing code fits the new domain exception

### 2. Domain layer

For each new aggregate, create under `domain/.../domain/{aggregate}/`:

```
{aggregate}/
├── {Entity}.kt                              # JPA entity
├── vo/                                      # Value objects (if needed)
├── exception/
│   └── {Entity}NotFoundException.kt         # Domain exception
└── repository/
    ├── {Entity}CommandRepository.kt         # Write interface
    ├── {Entity}CommandRepositoryImpl.kt     # Write impl (SimpleJpaRepository)
    ├── {Entity}QueryRepository.kt           # Read interface
    └── {Entity}QueryRepositoryImpl.kt       # Read impl (QueryDSL)
```

Entity pattern:
- Constructor `val` for identity fields, body `var` with `private set` for mutable fields
- `companion object { fun create(...) }` factory method
- Domain methods for state transitions (never expose setters)
- Extend `BaseEntity` for audit columns

Repository pattern:
- CommandRepository: `save()`, `delete()`, wraps `SimpleJpaRepository`
- QueryRepository: `findById()`, `findBy...()`, `existsBy...()`, uses `JPAQueryFactory`

### 3. Application layer

For each use case, create under `application/.../application/{feature}/`:

```
{feature}/
├── {Action}Service.kt                       # Use case impl
└── port/
    ├── in/
    │   ├── {Action}UseCase.kt               # Interface with operator fun invoke
    │   ├── command/
    │   │   └── {Action}Command.kt           # Write input DTO
    │   ├── query/
    │   │   └── {Entity}Query.kt             # Read input DTO
    │   └── result/
    │       └── {Entity}Result.kt            # Output DTO
    └── out/
        └── {Capability}Port.kt              # External dependency (if needed)
```

Rules:
- One UseCase interface = one Service class = one `operator fun invoke`
- Command for writes, Query for reads
- Result types only — never return domain entities
- `@Service` + `@Transactional` (or `readOnly = true` for queries)
- Entity→Result mapping via private extension functions in the service

### 4. Presentation layer

Create under `{presentation-module}/.../`:

```
{feature}/
├── {Feature}Controller.kt                   # @RestController
├── request/
│   ├── {Action}Request.kt                   # API input DTO
│   └── {Entity}PageRequest.kt               # Pagination DTO (if list endpoint)
└── response/
    └── {Entity}Response.kt                  # API output DTO
```

Controller pattern:
- `@RestController` + `@RequestMapping("/{feature-plural}")`
- Inject UseCase interfaces only
- Request→Command/Query and Result→Response via **private extension functions**
- Wrap all returns in `ApiResponse`

## After scaffolding

1. If a `database-administrator` agent exists, delegate to it for creating a Flyway migration
2. If a `dot-http` agent exists, delegate to it for creating `.http` test files
3. Run `./gradlew build` to verify compilation
4. Report the list of all created files to the user
