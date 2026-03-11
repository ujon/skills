# Application Layer Patterns

## Table of Contents
- [Package Structure](#package-structure)
- [Use Case Interface](#use-case-interface)
- [Command DTO](#command-dto)
- [Query DTO](#query-dto)
- [Result DTO](#result-dto)
- [Port Out Interface](#port-out-interface)
- [Service Implementation](#service-implementation)
- [Pagination](#pagination)

## Package Structure

Each feature domain gets its own package under `application/`:

```
application/src/main/kotlin/{base-package}/application/
└── {feature}/
    ├── {Action}Service.kt              # Use case implementation
    ├── port/
    │   ├── in/
    │   │   ├── {Action}UseCase.kt      # Use case interface
    │   │   ├── command/
    │   │   │   └── {Action}Command.kt  # Write input DTO
    │   │   ├── query/
    │   │   │   └── {Entity}Query.kt    # Read input DTO
    │   │   └── result/
    │   │       └── {Entity}Result.kt   # Output DTO
    │   └── out/
    │       └── {Capability}Port.kt     # External dependency interface
```

## Use Case Interface

Each use case represents a single action. Define it as an interface with `operator fun invoke`:

```kotlin
// port/in/CreateBookmarkUseCase.kt
interface CreateBookmarkUseCase {
    operator fun invoke(command: CreateBookmarkCommand): BookmarkResult
}

// port/in/GetBookmarksUseCase.kt
interface GetBookmarksUseCase {
    operator fun invoke(query: BookmarksQuery): PageResult<BookmarkResult>
}

// port/in/DeleteBookmarkUseCase.kt
interface DeleteBookmarkUseCase {
    operator fun invoke(command: DeleteBookmarkCommand)
}
```

Rules:
- One use case = one interface = one `invoke` method
- Write operations accept a `Command`, read operations accept a `Query`
- Return `Result` type (or `Unit` for void operations, `PageResult<Result>` for paginated reads)
- The `operator` keyword lets callers use `useCase(command)` syntax

## Command DTO

Commands represent write/action intent. They are simple `data class` types:

```kotlin
// port/in/command/CreateBookmarkCommand.kt
data class CreateBookmarkCommand(
    val userId: UUID,
    val postId: UUID,
)

// port/in/command/DeleteBookmarkCommand.kt
data class DeleteBookmarkCommand(
    val userId: UUID,
    val bookmarkId: UUID,
)
```

Rules:
- Named `{Action}Command` — the action verb describes what happens
- Pure data, no behavior or validation logic
- Fields use domain-appropriate types (UUID, not String for IDs)

## Query DTO

Queries represent read/query intent:

```kotlin
// port/in/query/BookmarksQuery.kt
data class BookmarksQuery(
    val userId: UUID,
    val page: Int,
    val size: Int,
)

// port/in/query/BookmarkDetailQuery.kt
data class BookmarkDetailQuery(
    val userId: UUID,
    val bookmarkId: UUID,
)
```

Rules:
- Named `{Entity}Query` or `{Entity}{Qualifier}Query`
- Include pagination params (`page`, `size`) when returning lists
- Include filter/sort criteria as needed

## Result DTO

Results carry data back from use cases. They must never expose domain entities directly:

```kotlin
// port/in/result/BookmarkResult.kt
data class BookmarkResult(
    val bookmarkId: UUID,
    val postId: UUID,
    val postTitle: String,
    val createdAt: Instant,
)
```

Rules:
- Named `{Entity}Result` or `{Entity}{Qualifier}Result`
- Flat structure preferred — denormalize what the consumer needs
- Use primitive/stdlib types, not domain entities
- Define a mapping extension function in the service (see below)

## Port Out Interface

When a use case needs an external capability not available in the domain layer, define a port/out:

```kotlin
// port/out/NotificationPort.kt
interface NotificationPort {
    fun sendPushNotification(userId: UUID, title: String, body: String)
}

// port/out/StoragePort.kt
interface StoragePort {
    fun upload(key: String, content: ByteArray, contentType: String): String
    fun delete(key: String)
}
```

Port/out adapters are implemented in the presentation module (or `infrastructure/*`):
- `{presentation-module}/.../common/security/JwtProvider.kt` implements `TokenProviderPort`
- `{presentation-module}/.../common/security/PasswordEncoderAdapter.kt` implements `PasswordEncoderPort`

## Service Implementation

Services implement use case interfaces and orchestrate domain logic:

```kotlin
// CreateBookmarkService.kt
@Service
class CreateBookmarkService(
    private val bookmarkCommandRepository: BookmarkCommandRepository,
    private val bookmarkQueryRepository: BookmarkQueryRepository,
    private val postQueryRepository: PostQueryRepository,
) : CreateBookmarkUseCase {

    @Transactional
    override fun invoke(command: CreateBookmarkCommand): BookmarkResult {
        // Validate preconditions
        val post = postQueryRepository.findById(command.postId)
            ?: throw PostNotFoundException()

        // Check for duplicates
        bookmarkQueryRepository.findByUserIdAndPostId(command.userId, command.postId)
            ?.let { throw ResourceAlreadyExistsException("Bookmark already exists") }

        // Execute domain logic
        val bookmark = Bookmark.create(
            userId = command.userId,
            postId = command.postId,
        )

        // Persist
        bookmarkCommandRepository.save(bookmark)

        // Map to result
        return bookmark.toResult(post.title)
    }

    private fun Bookmark.toResult(postTitle: String) = BookmarkResult(
        bookmarkId = bookmarkId,
        postId = postId,
        postTitle = postTitle,
        createdAt = createdAt!!,
    )
}
```

### Read service with pagination:

```kotlin
@Service
class GetBookmarksService(
    private val bookmarkQueryRepository: BookmarkQueryRepository,
) : GetBookmarksUseCase {

    @Transactional(readOnly = true)
    override fun invoke(query: BookmarksQuery): PageResult<BookmarkResult> {
        val pageable = PageRequest.of(query.page, query.size)
        return bookmarkQueryRepository.findByUserId(query.userId, pageable)
            .toPageResult { it.toResult() }
    }

    private fun Bookmark.toResult() = BookmarkResult(
        bookmarkId = bookmarkId,
        postId = postId,
        postTitle = "", // simplified
        createdAt = createdAt!!,
    )
}
```

Service rules:
- Annotated with `@Service`
- Constructor injection for all dependencies
- Implements exactly one use case interface
- `@Transactional` for writes, `@Transactional(readOnly = true)` for reads
- Entity-to-Result mapping via private extension functions
- Throws domain exceptions for business rule violations

## Pagination

Use the shared `PageResult` type for paginated results:

```kotlin
// common/PageResult.kt (already exists in application module)
data class PageResult<T>(
    val content: List<T>,
    val totalPages: Int,
    val number: Int,
    val isFirst: Boolean,
    val isLast: Boolean,
)

// Extension to convert Spring Page to PageResult
fun <T : Any, R> Page<T>.toPageResult(mapper: (T) -> R) = PageResult(
    content = content.map { mapper(it) },
    totalPages = totalPages,
    number = number,
    isFirst = isFirst,
    isLast = isLast,
)
```

Usage pattern:
1. Service receives `Query` with `page` and `size`
2. Creates `PageRequest.of(query.page, query.size)`
3. Repository returns `Page<Entity>`
4. Service converts via `.toPageResult { it.toResult() }`
5. Controller wraps with `ApiResponse.success(page = result, mapper = { it.toResponse() })`
