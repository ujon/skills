# Support Layer Patterns

## Table of Contents
- [Package Structure](#package-structure)
- [Exception Hierarchy](#exception-hierarchy)
- [ErrorCode Enum](#errorcode-enum)
- [Shared Type Enums](#shared-type-enums)
- [Adding a New Exception](#adding-a-new-exception)
- [Adding a New Shared Type](#adding-a-new-shared-type)

## Package Structure

```
support/src/main/kotlin/{base-package}/support/
├── exception/
│   ├── BaseException.kt            # Root exception class
│   ├── ErrorCode.kt                # Enum of all error codes
│   ├── LogSeverity.kt              # WARN, ERROR, INFO
│   ├── AccessDeniedException.kt
│   ├── ExpiredTokenException.kt
│   ├── InvalidTokenException.kt
│   ├── InvalidInputException.kt
│   ├── ResourceAlreadyExistsException.kt
│   ├── ResourceNotFoundException.kt
│   ├── UnauthorizedException.kt
│   └── InternalErrorException.kt
├── type/
│   ├── Role.kt                     # USER, ADMIN
│   ├── UserStatus.kt               # ACTIVE, INACTIVE, BANNED
│   ├── PostStatus.kt               # PUBLISHED, HIDDEN, DELETED
│   ├── CommentStatus.kt
│   ├── CategoryStatus.kt
│   ├── OauthProvider.kt            # GOOGLE, APPLE, KAKAO
│   ├── ReferenceType.kt
│   ├── TransactionType.kt
│   ├── CommentSource.kt
│   ├── FileReferenceType.kt
│   ├── StorageType.kt
│   └── HospitalStatus.kt
└── context/
    └── AuditorProvider.kt
```

## Exception Hierarchy

```
RuntimeException
  └── BaseException(errorCode, message, logSeverity)
        ├── [support] InvalidInputException       → INVALID_INPUT (400)
        ├── [support] UnauthorizedException        → UNAUTHORIZED (401)
        ├── [support] InvalidTokenException        → INVALID_TOKEN (401)
        ├── [support] ExpiredTokenException        → EXPIRED_TOKEN (401)
        ├── [support] AccessDeniedException        → ACCESS_DENIED (403)
        ├── [support] ResourceNotFoundException    → RESOURCE_NOT_FOUND (404)
        ├── [support] ResourceAlreadyExistsException → RESOURCE_ALREADY_EXISTS (409)
        ├── [support] InternalErrorException       → INTERNAL_ERROR (500)
        ├── [domain]  UserNotFoundException        → RESOURCE_NOT_FOUND (404)
        ├── [domain]  InvalidPasswordException     → UNAUTHORIZED (401)
        ├── [domain]  UserAlreadyExistsException   → RESOURCE_ALREADY_EXISTS (409)
        ├── [domain]  PostNotFoundException        → RESOURCE_NOT_FOUND (404)
        ├── [domain]  CommentNotFoundException     → RESOURCE_NOT_FOUND (404)
        └── [domain]  PointNotFoundException       → RESOURCE_NOT_FOUND (404)
```

### BaseException

```kotlin
open class BaseException(
    val errorCode: ErrorCode,
    override val message: String = errorCode.message,
    val logSeverity: LogSeverity = errorCode.logSeverity,
) : RuntimeException(message)
```

### Generic Support Exceptions

These live in `support/exception/` and can be used directly across all layers:

```kotlin
// For input validation failures
class InvalidInputException(
    message: String = "Invalid input",
) : BaseException(ErrorCode.INVALID_INPUT, message)

// For resource not found (generic, use domain-specific when possible)
class ResourceNotFoundException(
    message: String = "Resource not found",
) : BaseException(ErrorCode.RESOURCE_NOT_FOUND, message)

// For duplicate resource
class ResourceAlreadyExistsException(
    message: String = "Resource already exists",
) : BaseException(ErrorCode.RESOURCE_ALREADY_EXISTS, message)
```

## ErrorCode Enum

```kotlin
enum class ErrorCode(
    val statusCode: Int,
    val message: String,
    val logSeverity: LogSeverity = LogSeverity.WARN,
) {
    INVALID_INPUT(400, "Invalid input"),
    UNAUTHORIZED(401, "Unauthorized"),
    ACCESS_DENIED(403, "Access denied"),
    INVALID_TOKEN(401, "Invalid token"),
    EXPIRED_TOKEN(401, "Expired token"),
    RESOURCE_NOT_FOUND(404, "Resource not found", LogSeverity.INFO),
    RESOURCE_ALREADY_EXISTS(409, "Resource already exists"),
    INTERNAL_ERROR(500, "Internal server error", LogSeverity.ERROR),
}
```

When adding a new ErrorCode, consider:
- HTTP status code alignment (4xx for client errors, 5xx for server errors)
- Default log severity (INFO for expected conditions, WARN for client errors, ERROR for server errors)
- Whether an existing code already covers the case

## Shared Type Enums

Types that are referenced across multiple layers (domain, application, API) live in `support/type/`:

```kotlin
// support/type/PostStatus.kt
enum class PostStatus {
    PUBLISHED,
    HIDDEN,
    DELETED,
}

// support/type/Role.kt
enum class Role {
    USER,
    ADMIN,
}
```

Rules:
- Place in `support/type/` only if used across 2+ modules
- If an enum is only used within a single aggregate, it can stay in that aggregate's domain package
- Use `enum class` (not sealed class) for simple status/type enums
- Names should be self-descriptive without prefix (e.g., `PUBLISHED` not `POST_PUBLISHED`)

## Adding a New Exception

When your feature needs a new domain-specific exception:

1. Create in `domain/{aggregate}/exception/`:

```kotlin
// domain/bookmark/exception/BookmarkNotFoundException.kt
class BookmarkNotFoundException(
    message: String = "Bookmark not found",
) : BaseException(ErrorCode.RESOURCE_NOT_FOUND, message)
```

2. If no existing `ErrorCode` fits, add one to `support/exception/ErrorCode.kt` first.

3. The `ApiExceptionHandler` in the presentation module automatically catches all `BaseException` subclasses — no additional handler registration needed.

## Adding a New Shared Type

When your feature introduces a new enum used across layers:

1. Create in `support/type/`:

```kotlin
// support/type/BookmarkStatus.kt
enum class BookmarkStatus {
    ACTIVE,
    INACTIVE,
}
```

2. Reference from any module (domain entities, application DTOs, API responses).
