# Presentation Layer Patterns

The presentation layer is the outermost layer. A project can have multiple presentation modules (e.g., `*-api` for public endpoints, `*-admin` for back-office) — each is an independent Spring Boot application that shares the same `application`, `domain`, and `support` modules.

## Table of Contents
- [Package Structure](#package-structure)
- [Controller Pattern](#controller-pattern)
- [Request DTOs](#request-dtos)
- [Response DTOs](#response-dtos)
- [ApiResponse Wrapper](#apiresponse-wrapper)
- [Mapping Convention](#mapping-convention)
- [Authentication & User Context](#authentication--user-context)


## Package Structure

```
{presentation-module}/src/main/kotlin/{base-package}/{presentation}/
├── {feature}/
│   ├── {Feature}Controller.kt
│   ├── request/
│   │   ├── {Action}Request.kt
│   │   └── {Entity}PageRequest.kt
│   └── response/
│       ├── {Entity}Response.kt
│       └── {Entity}DetailResponse.kt
├── common/
│   ├── response/
│   │   └── ApiResponse.kt
│   ├── exception/
│   │   └── ApiExceptionHandler.kt
│   ├── security/
│   │   ├── JwtProvider.kt           # TokenProviderPort adapter
│   │   ├── PasswordEncoderAdapter.kt # PasswordEncoderPort adapter
│   │   └── UserPrincipal.kt
│   ├── context/
│   │   ├── HeaderContext.kt
│   │   └── HeaderContextFilter.kt
│   └── config/
│       ├── SecurityConfig.kt
│       └── ...
```

## Controller Pattern

Controllers are thin — they map DTOs and delegate to use cases:

```kotlin
@RestController
@RequestMapping("/bookmarks")
class BookmarkController(
    private val createBookmarkUseCase: CreateBookmarkUseCase,
    private val getBookmarksUseCase: GetBookmarksUseCase,
    private val deleteBookmarkUseCase: DeleteBookmarkUseCase,
) {

    @PostMapping
    fun create(
        @AuthenticationPrincipal principal: UserPrincipal,
        @Valid @RequestBody request: CreateBookmarkRequest,
    ): ApiResponse<BookmarkResponse> =
        request.toCommand(principal.userId)
            .let(createBookmarkUseCase::invoke)
            .toResponse()
            .let { ApiResponse.success(it) }

    @GetMapping
    fun getBookmarks(
        @AuthenticationPrincipal principal: UserPrincipal,
        request: BookmarkPageRequest,
    ): ApiResponse<List<BookmarkResponse>> {
        val result = getBookmarksUseCase(request.toQuery(principal.userId))
        return ApiResponse.success(
            page = result,
            mapper = { it.toResponse() },
        )
    }

    @DeleteMapping("/{bookmarkId}")
    fun delete(
        @AuthenticationPrincipal principal: UserPrincipal,
        @PathVariable bookmarkId: UUID,
    ): ApiResponse<Nothing> {
        deleteBookmarkUseCase(DeleteBookmarkCommand(principal.userId, bookmarkId))
        return ApiResponse.success()
    }

    // --- Private mapping extension functions ---

    private fun CreateBookmarkRequest.toCommand(userId: UUID) = CreateBookmarkCommand(
        userId = userId,
        postId = postId,
    )

    private fun BookmarkPageRequest.toQuery(userId: UUID) = BookmarksQuery(
        userId = userId,
        page = page,
        size = size,
    )

    private fun BookmarkResult.toResponse() = BookmarkResponse(
        bookmarkId = bookmarkId,
        postId = postId,
        postTitle = postTitle,
        createdAt = createdAt,
    )
}
```

Controller rules:
- `@RestController` + `@RequestMapping("/{feature-plural}")`
- Constructor injection of use case interfaces only (no repositories, no services directly)
- Expression body (`=`) for simple endpoints, block body for multi-step
- All mapping logic in private extension functions at the bottom

## Request DTOs

Request DTOs live in `{feature}/request/` and carry client input:

```kotlin
// request/CreateBookmarkRequest.kt
data class CreateBookmarkRequest(
    @field:NotNull(message = "Post ID is required")
    val postId: UUID,
)
```

```kotlin
// request/BookmarkPageRequest.kt
data class BookmarkPageRequest(
    val page: Int = 0,
    val size: Int = 20,
)
```

Rules:
- Use `@field:` prefix for Bean Validation annotations (Kotlin property mapping)
- Request classes never contain mapping logic — that belongs in the controller

## Response DTOs

Response DTOs live in `{feature}/response/`:

```kotlin
// response/BookmarkResponse.kt
data class BookmarkResponse(
    val bookmarkId: UUID,
    val postId: UUID,
    val postTitle: String,
    val createdAt: Instant,
)
```

Rules:
- Response classes are pure data — no mapping logic inside
- May differ from Result DTOs (e.g., formatting dates, nesting differently)

## ApiResponse Wrapper

All API responses use the `ApiResponse` wrapper:

```kotlin
// Success with payload
ApiResponse.success(payload)

// Success with no payload (e.g., delete)
ApiResponse.success()

// Success with paginated payload
ApiResponse.success(page = pageResult, mapper = { it.toResponse() })

// Error
ApiResponse.error("Something went wrong")
```

The wrapper provides:
- `message: String` — always present
- `payload: T?` — nullable, only for success with data
- `isFirst: Boolean?` / `isLast: Boolean?` — pagination metadata

## Mapping Convention

The flow through a controller endpoint:

```
Request → Command/Query → UseCase → Result → Response → ApiResponse
```

All conversions happen via **private extension functions** inside the controller:
- `Request.toCommand(...)` — may take additional params like `userId`
- `Request.toQuery(...)` — may take additional params
- `Result.toResponse()` — pure mapping

This keeps the API layer's DTO mapping isolated from both the Request class and the application layer. The Request class doesn't know about Commands, and the application layer doesn't know about Responses.

## Authentication & User Context

Use `@AuthenticationPrincipal` to access the authenticated user:

```kotlin
@PostMapping
fun create(
    @AuthenticationPrincipal principal: UserPrincipal,
    @Valid @RequestBody request: CreateBookmarkRequest,
): ApiResponse<BookmarkResponse> { ... }
```

`UserPrincipal` provides:
- `userId: UUID`
- `role: String`
- Other claims from the JWT token

For optional authentication (public + authenticated endpoints):

```kotlin
@GetMapping("/{postId}")
fun getPost(
    @AuthenticationPrincipal principal: UserPrincipal?,
    @PathVariable postId: UUID,
): ApiResponse<PostDetailResponse> { ... }
```

### Locale Handling

When locale-dependent data is needed, accept `Locale` parameter:

```kotlin
@GetMapping("/categories")
fun getCategories(locale: Locale): ApiResponse<List<CategoryResponse>> { ... }
```

