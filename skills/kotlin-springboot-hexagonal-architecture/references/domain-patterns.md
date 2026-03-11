# Domain Layer Patterns

## Table of Contents
- [Entity Pattern](#entity-pattern)
- [Base Entity (Audit)](#base-entity-audit)
- [Value Objects](#value-objects)
- [Domain Exceptions](#domain-exceptions)
- [Repository Pattern](#repository-pattern)
- [Domain Service Pattern](#domain-service-pattern)
- [Spec & Info Pattern](#spec--info-pattern)

## Entity Pattern

Entities are JPA `@Entity` classes that encapsulate domain logic. Mutable fields use `private set` to enforce invariants through domain methods.

```kotlin
@Entity
@Table(name = "tbl_bookmark")
class Bookmark(
    @Id
    @Column(name = "bookmark_id")
    val bookmarkId: UUID = UUID.randomUUID(),

    @Column(name = "user_id", nullable = false)
    val userId: UUID,

    @Column(name = "post_id", nullable = false)
    val postId: UUID,

    status: BookmarkStatus = BookmarkStatus.ACTIVE,
) : BaseEntity() {

    @Column(name = "status", nullable = false, length = 20)
    var status: BookmarkStatus = status
        private set

    // Domain methods for state transitions
    fun activate() {
        this.status = BookmarkStatus.ACTIVE
    }

    fun deactivate() {
        this.status = BookmarkStatus.INACTIVE
    }

    // Factory method
    companion object {
        fun create(userId: UUID, postId: UUID) = Bookmark(
            userId = userId,
            postId = postId,
        )
    }
}
```

Key rules:
- Immutable identity fields declared as constructor `val` parameters
- Mutable fields declared in the body with `private set`
- State transitions through named domain methods, not direct setters
- `companion object` with `create()` factory for construction
- Always extend `BaseEntity` for audit columns
- Table and schema naming should follow the project's existing conventions

### Counter Fields

For denormalized counters (like count, viewCount), use domain methods with invariant checks:

```kotlin
@Column(name = "like_count", nullable = false)
var likeCount: Long = 0
    private set

fun incrementLikeCount() {
    this.likeCount++
}

fun decrementLikeCount() {
    require(likeCount > 0) { "Like count cannot be negative" }
    this.likeCount--
}
```

## Base Entity (Audit)

All entities extend `BaseEntity` which provides automatic audit columns:

```kotlin
@MappedSuperclass
@EntityListeners(AuditingEntityListener::class)
abstract class BaseEntity {
    @CreatedDate
    @Column(name = "created_at", updatable = false)
    var createdAt: Instant? = null
        protected set

    @CreatedBy
    @Column(name = "created_by", updatable = false, length = 36)
    var createdBy: String? = null
        protected set

    @LastModifiedDate
    @Column(name = "updated_at")
    var updatedAt: Instant? = null
        protected set

    @LastModifiedBy
    @Column(name = "updated_by", length = 36)
    var updatedBy: String? = null
        protected set
}
```

For entities that only need creation audit (no updates), use `CreatedBaseEntity` instead.

## Value Objects

Use `@JvmInline value class` for type-safe value objects with validation in `init`:

```kotlin
// domain/{aggregate}/vo/{ValueObject}.kt
@JvmInline
value class Email(val value: String) {
    init {
        require(value.matches(EMAIL_REGEX)) { "Invalid email format: $value" }
    }

    companion object {
        private val EMAIL_REGEX = Regex("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")
    }
}
```

Value objects are ideal for:
- IDs with specific formats
- Strings with validation rules (email, username, phone)
- Numeric types with constraints (positive amounts, percentages)

## Domain Exceptions

Each aggregate defines its own exceptions extending `BaseException`:

```kotlin
// domain/{aggregate}/exception/{Entity}NotFoundException.kt
class BookmarkNotFoundException(
    message: String = "Bookmark not found",
) : BaseException(ErrorCode.RESOURCE_NOT_FOUND, message)
```

Rules:
- Place in `domain/{aggregate}/exception/`
- Extend `BaseException` from support module
- Map to appropriate `ErrorCode` enum value
- Provide sensible default message
- Keep constructor simple — usually just a message override

Common exception patterns:
| Situation | ErrorCode | Naming |
|-----------|-----------|--------|
| Entity not found | `RESOURCE_NOT_FOUND` | `{Entity}NotFoundException` |
| Duplicate entity | `RESOURCE_ALREADY_EXISTS` | `{Entity}AlreadyExistsException` |
| Invalid domain state | `INVALID_INPUT` | `Invalid{Field}Exception` |
| Auth failure | `UNAUTHORIZED` | `Invalid{Credential}Exception` |

## Repository Pattern

Repositories are split into **Command** (write) and **Query** (read) — a CQRS-style separation.

### Command Repository

```kotlin
// Interface
interface BookmarkCommandRepository {
    fun save(bookmark: Bookmark): Bookmark
    fun delete(bookmark: Bookmark)
}

// Implementation using SimpleJpaRepository
@Repository
class BookmarkCommandRepositoryImpl(
    entityManager: EntityManager,
) : BookmarkCommandRepository {

    private val jpaRepository = SimpleJpaRepository<Bookmark, UUID>(
        Bookmark::class.java, entityManager
    )

    override fun save(bookmark: Bookmark): Bookmark = jpaRepository.save(bookmark)
    override fun delete(bookmark: Bookmark) = jpaRepository.delete(bookmark)
}
```

### Query Repository

```kotlin
// Interface
interface BookmarkQueryRepository {
    fun findByUserIdAndPostId(userId: UUID, postId: UUID): Bookmark?
    fun findByUserId(userId: UUID, pageable: Pageable): Page<Bookmark>
    fun existsByUserIdAndPostId(userId: UUID, postId: UUID): Boolean
}

// Implementation using QueryDSL
@Repository
class BookmarkQueryRepositoryImpl(
    private val queryFactory: JPAQueryFactory,
) : BookmarkQueryRepository {

    override fun findByUserIdAndPostId(userId: UUID, postId: UUID): Bookmark? =
        queryFactory.selectFrom(bookmark)
            .where(
                bookmark.userId.eq(userId),
                bookmark.postId.eq(postId),
            )
            .fetchOne()

    override fun findByUserId(userId: UUID, pageable: Pageable): Page<Bookmark> {
        val content = queryFactory.selectFrom(bookmark)
            .where(bookmark.userId.eq(userId))
            .offset(pageable.offset)
            .limit(pageable.pageSize.toLong())
            .orderBy(bookmark.createdAt.desc())
            .fetch()

        val total = queryFactory.select(bookmark.count())
            .from(bookmark)
            .where(bookmark.userId.eq(userId))
            .fetchOne() ?: 0L

        return PageImpl(content, pageable, total)
    }

    override fun existsByUserIdAndPostId(userId: UUID, postId: UUID): Boolean =
        queryFactory.selectOne()
            .from(bookmark)
            .where(
                bookmark.userId.eq(userId),
                bookmark.postId.eq(postId),
            )
            .fetchFirst() != null
}
```

Key rules:
- Both interface and implementation live in `domain/{aggregate}/repository/`
- CommandRepository: uses `SimpleJpaRepository` wrapper
- QueryRepository: uses `JPAQueryFactory` (QueryDSL) for type-safe queries
- `@Repository` annotation on implementations
- Constructor injection for `EntityManager` (command) and `JPAQueryFactory` (query)

## Domain Service Pattern

When business logic spans multiple aggregates or requires complex coordination, use a domain service:

```kotlin
@Component
class PointDomainService(
    private val pointQueryRepository: PointQueryRepository,
) {
    fun earn(spec: EarnSpec): PointInfo {
        val point = pointQueryRepository.findByUserId(spec.userId)
            ?: Point.create(spec.userId)
        point.earn(spec.amount)

        val transaction = PointTransaction.earn(
            userId = point.userId,
            amount = spec.amount,
            pointSnapshot = point.availablePoint,
            referenceType = spec.referenceType,
            referenceId = spec.referenceId,
            expiredAt = spec.expiredAt,
        )

        return PointInfo(point, transaction)
    }
}
```

Domain services:
- Annotated with `@Component` (not `@Service`, which is reserved for application services)
- Coordinate logic across multiple entities within the same bounded context
- Return domain-level info objects (not application-level Results)
- Do NOT manage transactions — that's the application service's job

## Spec & Info Pattern

**Spec** classes package input parameters for domain services:

```kotlin
// domain/{aggregate}/spec/{Action}Spec.kt
data class EarnSpec(
    val userId: UUID,
    val amount: Long,
    val referenceType: ReferenceType? = null,
    val referenceId: UUID? = null,
    val expiredAt: Instant? = null,
)
```

**Info** classes return composite results from domain services:

```kotlin
// domain/{aggregate}/info/{Entity}Info.kt
data class PointInfo(
    val point: Point,
    val transaction: PointTransaction,
)
```

Use Spec/Info when a domain service needs structured input/output that doesn't fit a single entity.
