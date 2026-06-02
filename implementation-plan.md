# Backend Implementation Roadmap

## B.Tech EE-VLSI Legacy Platform — FastAPI + PostgreSQL + Firebase Auth/Storage + Redis

> [!NOTE]
> This roadmap is sequenced so that each milestone produces a **testable, independently verifiable deliverable**. You should be able to hit every endpoint in Swagger UI before moving to the next milestone. The frontend is irrelevant until this entire roadmap is green.

### Revised Stack

| Concern | Technology | Role |
|---|---|---|
| API Framework | FastAPI (ASGI) | Request routing, validation, dependency injection |
| Structured Data | **PostgreSQL 16** via **SQLAlchemy 2.0 (async)** + **Alembic** | All relational data — users, announcements, resources, events, projects |
| Identity Provider | Firebase Auth | Sign-in, JWT issuance, custom claims (RBAC) |
| Binary Object Store | Firebase Cloud Storage | PDFs, images, gallery media |
| Message Broker | Redis | Async task queue for webhook dispatch |
| Background Worker | Raw Python consumer process | Processes queued tasks (WhatsApp webhook) |

```text
                               ┌──────────────────────────────────┐
                               │       Firebase Platform          │
                               ├──────────────────────────────────┤
                     ┌────────>│  • Firebase Auth (IdP)           │
                     │         │  • Cloud Storage (Object Store)  │
                     │         └──────────────────────────────────┘
                     │                           ▲
  ┌──────────────────┴───┐                       │ (Admin SDK: claims, signed URLs)
  │  React Client (SPA)  │                       │
  └──────────────────┬───┘                       │
                     │                           │
                     │                 ┌─────────┴────────┐
                     └────────────────>│   Python FastAPI  │
                       (HTTPS + JWT)   │   (API Gateway)   │
                                       └──┬───────────┬───┘
                                          │           │
                                 (SQL)    │           │ (Task Push)
                                          ▼           ▼
                               ┌──────────────┐  ┌──────────────────┐
                               │ PostgreSQL   │  │   Redis Broker   │
                               │ (Relational) │  └─────────┬────────┘
                               └──────────────┘            │ (BLPOP)
                                                           ▼
                                                 ┌──────────────────┐      ┌────────────────────┐
                                                 │  Background      ├─────>│ WhatsApp Community │
                                                 │  Worker Process  │      │  Webhook API       │
                                                 └──────────────────┘      └────────────────────┘
```

---

## Milestone 0 — Project Scaffolding & Environment Isolation ✅ COMPLETE

### Core Objective
Stand up a reproducible Python project structure with dependency isolation, environment-variable-driven configuration, and a running FastAPI dev server that returns a health check.

### System Design Checklist

#### Directory Structure Target
```
ee-vlsi-platform/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app factory & lifespan events
│   ├── config.py                # Pydantic Settings (env-driven config)
│   ├── dependencies.py          # Shared FastAPI dependency callables
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py        # Top-level v1 API router (includes sub-routers)
│   ├── core/                    # Cross-cutting: auth, RBAC, exceptions
│   │   └── __init__.py
│   ├── db/                      # Database engine, session, ORM base
│   │   ├── __init__.py
│   │   ├── engine.py            # SQLAlchemy async engine + session factory
│   │   ├── base.py              # Declarative base class for ORM models
│   │   └── models/              # SQLAlchemy ORM table definitions
│   │       ├── __init__.py
│   │       └── ...
│   ├── schemas/                 # Pydantic DTOs (request/response shapes)
│   │   └── __init__.py
│   ├── repositories/            # Data access layer (SQL queries via session)
│   │   └── __init__.py
│   ├── services/                # Business logic orchestration
│   │   └── __init__.py
│   └── workers/                 # Redis consumer & task definitions
│       └── __init__.py
├── alembic/                     # Alembic migration environment
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                # Auto-generated migration files
├── firebase/
│   └── storage.rules            # Cloud Storage security rules
├── tests/
│   └── __init__.py
├── scripts/                     # One-off dev utilities (seed data, set claims)
├── .env.example                 # Template for required env vars
├── .gitignore
├── alembic.ini                  # Alembic configuration
├── pyproject.toml               # Or requirements.txt
├── Dockerfile
└── docker-compose.yml
```

> [!IMPORTANT]
> Notice the separation: `app/db/models/` holds **SQLAlchemy ORM classes** (your database table definitions). `app/schemas/` holds **Pydantic models** (your API request/response shapes). These are different things. Don't mix them. A route receives a Pydantic schema, passes it to a service, which calls a repository that works with SQLAlchemy models. Data flows: `Schema → Service → Repository → ORM Model → Database`.

#### Configuration Tasks
- [X] Initialize a Python virtual environment (`python -m venv .venv`)
- [X] Install core dependencies: `fastapi`, `uvicorn[standard]`, `pydantic-settings`, `python-dotenv`
- [X] Create `app/config.py` using Pydantic's `BaseSettings` to load all secrets from `.env`
  - Required vars at this stage: `PROJECT_NAME`, `DEBUG`, `API_V1_PREFIX`, `CORS_ORIGINS`
- [X] Create `app/main.py` with an application factory function that:
  - Instantiates `FastAPI(lifespan=...)` using the async lifespan context manager pattern (not deprecated `on_event`)
  - Mounts the v1 router under `/api/v1`
  - Registers CORS middleware
- [X] Create a single `GET /api/v1/health` endpoint returning `{"status": "operational", "version": "0.1.0"}`
- [X] Create `.env.example` and add `.env` to `.gitignore` immediately
- [X] Initialize git repo with an initial commit

### Testing & Verification
1. Run `uvicorn app.main:app --reload`
2. Navigate to `http://localhost:8000/docs` — Swagger UI should render
3. Hit the `/api/v1/health` endpoint from both Swagger and a `curl`/Postman request
4. Confirm environment variables load correctly by adding a debug log on startup

### Conceptual Pitfalls

> [!WARNING]
> **Lifespan vs. `on_event`**: FastAPI's `@app.on_event("startup")` is deprecated. Use the `lifespan` async context manager from day one. This is where you'll later initialize the SQLAlchemy engine, Firebase Admin SDK, and Redis connection pools. Getting this wrong now means refactoring later.

> [!CAUTION]
> **Secret Leakage**: Never hardcode Firebase service account paths, database URLs, or API keys. Use `pydantic-settings` with `env_file = ".env"` and mark sensitive fields with `SecretStr`. Add `.env` to `.gitignore` before your first commit — not after.

- **Flat vs. Layered structure**: The `api → services → repositories` layering is deliberate. Routes should *never* import SQLAlchemy sessions directly. If you skip this discipline now, you'll pay for it when writing tests (you can't mock what isn't abstracted).
- **CORS early**: Configure `allow_origins` from your env config immediately. When the React frontend connects later, a missing CORS header will produce a cryptic browser error that looks like a network failure, not a CORS issue.

---

### 🔍 M0 Review Findings — Fix Before Starting M1

These are minor issues found during review. Address them before moving on:

- [X] **Move health endpoint into the v1 router**: Currently the health route is defined directly on `app` in `main.py` (line 37). It should live in `app/api/v1/router.py` using an `APIRouter`, and `main.py` should `include_router(api_v1_router, prefix=settings.API_V1_PREFIX)`. The commented-out line 31 in `main.py` shows you intended this — finish wiring it.
- [X] **Broaden `.gitignore`**: Currently only ignores `app/__pycache__/`, but `__pycache__/` dirs will appear in `app/db/`, `app/api/v1/`, `app/core/`, etc. Change to `**/__pycache__/`. Also add `.venv/` — it's currently unignored and could accidentally get committed.
- [X] **Fix `env_file` path in `config.py`**: `env_file="../.env"` is relative to the working directory, not the file location. When you run `uvicorn app.main:app` from the project root, the `.env` is at `./.env`, not `../.env`. Change to `env_file=".env"`. This will break in Docker if not fixed now.

---

## Milestone 1 — PostgreSQL + SQLAlchemy + Alembic Bootstrap ✅ COMPLETE

> **M1 Review**: All items verified — engine, session factory, Base, TimestampMixin, Batch model, Alembic async env.py, first migration, Pydantic schemas, repository, route endpoints, Firebase init. Solid work.

> [!WARNING]
> **Double prefix bug**: Your batch router in `api/v1/batch.py` has `prefix="/batches"`, and `router.py` also adds `prefix="/batches"` in `include_router()`. This means the actual URL is `/api/v1/batches/batches`. Remove the prefix from the `include_router()` call in `router.py` (let each sub-router own its own prefix).

### Core Objective
Stand up a PostgreSQL database in Docker, configure SQLAlchemy 2.0 async engine and session management, set up Alembic for schema migrations, define your first ORM model (`batches`), and verify the full round-trip: migration → insert → query → API response.

### System Design Checklist

#### Infrastructure Setup
- [X] Start PostgreSQL via Docker:
  ```bash
  docker run -d --name ee-vlsi-db -p 5432:5432 \
    -e POSTGRES_USER=vlsi_dev \
    -e POSTGRES_PASSWORD=devpass123 \
    -e POSTGRES_DB=ee_vlsi_platform \
    postgres:16-alpine
  ```
- [X] Add database settings to `app/config.py`:
  - `DATABASE_URL`: `postgresql+asyncpg://vlsi_dev:devpass123@localhost:5432/ee_vlsi_platform`
  - Note: the `+asyncpg` dialect suffix is what makes SQLAlchemy use the async driver

#### SQLAlchemy Engine & Session
- [X] `app/db/engine.py`:
  - Create an `AsyncEngine` using `create_async_engine(settings.DATABASE_URL)`
  - Create an `async_sessionmaker` bound to that engine — this is your session factory
  - Create a `get_db_session()` async generator dependency that yields an `AsyncSession` and handles commit/rollback in a try/finally
  - Wire engine creation into `lifespan` (create on startup, dispose on shutdown)
- [X] `app/db/base.py`:
  - Define a `Base` class using SQLAlchemy's `DeclarativeBase`
  - Add common mixins if desired (e.g., `TimestampMixin` with `created_at` / `updated_at` columns that auto-populate)

#### First ORM Model
- [X] `app/db/models/batch.py`:
  ```python
  # Conceptual shape — you write the actual implementation
  class Batch(Base):
      __tablename__ = "batches"
      id: Mapped[int]              # Primary key, autoincrement
      batch_year: Mapped[int]      # Unique, not null
  ```
  - Use SQLAlchemy 2.0's `Mapped[]` type annotation style, not the legacy `Column()` style. The 2.0 style gives you type checker integration and is the modern standard.

#### Alembic Setup
- [X] Initialize Alembic: `alembic init alembic`
- [X] Configure `alembic.ini`: set `sqlalchemy.url` to your database URL (or better: read it from your `.env` inside `alembic/env.py`)
- [X] Modify `alembic/env.py`:
  - Import your `Base` metadata
  - Import ALL your model modules (so Alembic can see them for autogeneration)
  - Configure the async engine for migrations (Alembic has an async migration runner pattern)
- [X] Generate your first migration: `alembic revision --autogenerate -m "create_batches_table"`
- [X] Review the generated migration file — **never blindly apply autogenerated migrations**
- [X] Apply: `alembic upgrade head`

#### First Endpoints
- [ ] `app/schemas/batch.py`:
  - `BatchCreate`: `batch_year: int`
  - `BatchResponse`: `id: int`, `batch_year: int`
- [ ] `app/repositories/batch_repository.py`:
  - `create(session, data)` — Insert with uniqueness check
  - `get_all(session)` — Return all batches ordered by year
- [ ] `app/api/v1/batches.py`:
  - `POST /api/v1/batches` — Create batch (Admin-only later, unprotected for now)
  - `GET /api/v1/batches` — List all batches

#### SQLAlchemy Session Dependency Pattern

> [!TIP]
> This is the single most important pattern in your codebase. Every route that touches the database will use it:
> ```python
> # Conceptual shape for your get_db_session dependency
> async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
>     async with async_session_factory() as session:
>         try:
>             yield session
>             await session.commit()
>         except Exception:
>             await session.rollback()
>             raise
> ```
> Routes inject this via `Depends(get_db_session)`, and pass the session to repositories. The repository never creates or commits sessions — it only uses the one it's given. This keeps transaction boundaries at the route/service layer.

### Also: Firebase Admin SDK Init (Unchanged from TAD)
- [ ] `app/core/firebase.py`:
  - Initialize `firebase_admin.initialize_app(cred)` using a service account JSON
  - Expose helpers: `get_auth_client()`, `get_storage_bucket()`
  - Guard against double-initialization
- [ ] Add to `app/config.py`:
  - `FIREBASE_SERVICE_ACCOUNT_PATH`
  - `FIREBASE_PROJECT_ID`
  - `FIREBASE_STORAGE_BUCKET`
- [ ] Wire Firebase init into `lifespan` alongside the SQLAlchemy engine

### Testing & Verification
1. Confirm PostgreSQL is running: `docker exec -it ee-vlsi-db psql -U vlsi_dev -d ee_vlsi_platform -c '\dt'`
2. Run `alembic upgrade head` — should create the `batches` table
3. Verify in psql: `SELECT * FROM batches;` — empty table, correct columns
4. Seed a batch via `POST /api/v1/batches` from Swagger → confirm `201`
5. Retrieve via `GET /api/v1/batches` → confirm the round-trip
6. Post a duplicate `batch_year` → confirm `409 Conflict` (your uniqueness constraint should catch this)
7. Kill the server, remove `DATABASE_URL` from `.env`, restart → confirm the app fails fast with a clear error, not a cryptic traceback

### Conceptual Pitfalls

> [!CAUTION]
> **Sync vs. Async confusion**: SQLAlchemy 2.0 has two modes. You want the **async** mode using `create_async_engine` + `AsyncSession` + `asyncpg` driver. If you accidentally import from `sqlalchemy` instead of `sqlalchemy.ext.asyncio`, you'll get synchronous objects that block FastAPI's event loop. The imports matter:
> ```python
> # CORRECT — async
> from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
>
> # WRONG — sync (will block the event loop)
> from sqlalchemy import create_engine
> from sqlalchemy.orm import Session, sessionmaker
> ```

> [!WARNING]
> **Alembic + async requires extra wiring**. Alembic's default `env.py` template is synchronous. You need to modify it to use `run_async()` with your async engine. The SQLAlchemy docs have an explicit "Using Asyncio with Alembic" guide — follow it precisely. If your `env.py` uses a sync engine, migrations will work but won't match your runtime engine configuration.

- **`Mapped[]` type hints**: SQLAlchemy 2.0's `Mapped[int]` with `mapped_column()` replaces the old `Column(Integer)` style. Mixing styles within a project creates confusion. Pick 2.0 style and stick with it.
- **Session scope**: One session per request. Don't create a global session. Don't share sessions across requests. The `get_db_session` dependency creates a fresh session per request and handles cleanup.
- **Migration discipline**: Never modify a migration file after it's been applied. If you need to change a table, create a new migration. If you mess up locally, `alembic downgrade -1`, delete the migration file, fix your model, and regenerate.
- **Enum types in PostgreSQL**: Your schema uses enums (`role_enum`, `approval_status_enum`, `material_type_enum`). PostgreSQL has native ENUM types. SQLAlchemy can create them, but **Alembic doesn't auto-detect enum value changes**. If you add a value to an enum later, you'll need a manual migration with `ALTER TYPE ... ADD VALUE`. Be aware of this from the start.

---

## Milestone 2 — Authentication Middleware & Token Verification ✅ COMPLETE

> **M2 Review**: Auth dependency chain working — `verify_firebase_token` → `get_current_user`. User ORM model with PostgreSQL ENUMs, registration flow, `/me` endpoint, migration applied. Firebase Admin SDK properly used for token verification. See review findings below.

> [!WARNING]
> **Issues to fix:**
> 1. **`firestore_uid` naming**: The parameter in `auth_repository.py` line 11 is named `firestore_uid` — but you're not using Firestore anymore. It should be `firebase_uid` to match your column name. A small typo but it'll confuse future-you.
> 2. **Double commit**: In `api/v1/auth.py` line 29, you call `await db.commit()` manually, but your `get_db_session` dependency ALSO commits after the route handler returns. This means you're committing twice. Remove the manual `db.commit()` from the route — the dependency handles it. The `db.refresh(user)` on line 30 is also unnecessary if `expire_on_commit=False` is set (which it is in your engine.py).
> 3. **Missing `back_populates` on Batch model**: `User` has `batch: relationship("Batch", back_populates="users")` but `Batch` model doesn't have a `users` relationship. Add `users: Mapped[list["User"]] = relationship(back_populates="batch")` to Batch, or remove `back_populates` from User.
> 4. **`TokenPayload` schema is defined but not used as a type**: In `auth.py` route, you type-hint `token_payload: TokenPayload = Depends(verify_firebase_token)`, but `verify_firebase_token` returns a raw dict (the decoded Firebase token), not a `TokenPayload` instance. This works at runtime because Python doesn't enforce type hints, but it's semantically misleading. Either construct a `TokenPayload` inside `verify_firebase_token`, or type-hint the parameter as `dict`.

### Core Objective
Build a reusable FastAPI dependency that intercepts the `Authorization: Bearer <JWT>` header, cryptographically verifies the Firebase ID token, and injects the decoded user identity into the request context. After this milestone, you should be able to protect any route with a single `Depends()` call.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/core/auth.py` — The authentication dependency module:
  - Define `HTTPBearer` security scheme
  - Implement `verify_firebase_token(credentials)` dependency:
    - Extract the raw JWT from `Authorization: Bearer <token>`
    - Call `firebase_admin.auth.verify_id_token(token)` — this handles JWK fetching, signature verification, expiration, issuer, and audience checks *for you*
    - Return the decoded token payload dict
  - Implement `get_current_user(token_payload, db_session)` dependency:
    - Extract `uid` from the decoded token
    - Query the `users` table in PostgreSQL by `firebase_uid`
    - Return a Pydantic `CurrentUser` model or raise `404` if user not found
- [ ] `app/schemas/auth.py` — Pydantic schemas:
  - `TokenPayload`: Represents the decoded JWT claims you care about (`uid`, `email`, `role`, `email_verified`)
  - `CurrentUser`: The enriched user model combining token claims + PostgreSQL profile data
- [ ] `app/schemas/user.py` — User domain schemas:
  - `UserCreate`: Input schema for registration
  - `UserResponse`: Public-facing user data (exclude internal fields)
- [x] `app/db/models/user.py` — SQLAlchemy ORM model:
  ```python
  # Conceptual shape
  class User(Base):
      __tablename__ = "users"
      id: Mapped[uuid.UUID]         # PK, server_default=gen_random_uuid()
      firebase_uid: Mapped[str]     # Unique — links to Firebase Auth
      name: Mapped[str]
      email: Mapped[str]            # Unique
      roll_number: Mapped[str]      # Unique
      batch_id: Mapped[int]         # FK → batches.id
      role: Mapped[RoleEnum]        # PostgreSQL ENUM
      profile_photo_url: Mapped[Optional[str]]
      github_url: Mapped[Optional[str]]
      linkedin_url: Mapped[Optional[str]]
      approval_status: Mapped[ApprovalStatusEnum]  # Default PENDING
      created_at: Mapped[datetime]  # server_default=now()
      updated_at: Mapped[datetime]  # onupdate=now()
  ```
- [ ] Generate and apply migration: `alembic revision --autogenerate -m "create_users_table"`
- [ ] `app/api/v1/auth.py` — Auth-related endpoints:
  - `POST /api/v1/auth/register` — Accepts a Firebase ID token + profile payload, creates the user row in PostgreSQL
  - `GET /api/v1/auth/me` — Returns the current authenticated user's profile (test endpoint)

#### Dependency Chain Architecture
```
Route Handler
  └── Depends(get_current_user)
        ├── Depends(verify_firebase_token)
        │     └── Depends(HTTPBearer())
        └── Depends(get_db_session)
```

> [!TIP]
> FastAPI resolves dependency chains automatically. You only need to declare the outermost dependency (`get_current_user`) on your route. FastAPI walks the chain upward, resolving `verify_firebase_token` and `get_db_session` first, then passing both results into `get_current_user`.

#### Key Design Decision: `firebase_uid` as Lookup Key, UUID as PK

> [!IMPORTANT]
> Your PostgreSQL `users` table should have its own UUID primary key (`id`) for relational integrity (foreign keys from `announcements.author_id`, `projects.author_id`, etc.), **plus** a unique `firebase_uid` column that links to Firebase Auth. The `get_current_user` dependency queries by `firebase_uid` (from the JWT), but all internal foreign keys reference the PostgreSQL `id`. This keeps your relational schema clean while maintaining the Firebase Auth link.

### Testing & Verification

Since you don't have a React frontend, you need to **generate a valid Firebase ID token manually**:

1. **Create a test user** in Firebase Console → Authentication → Add User (email/password)
2. **Get an ID token** using the Firebase Auth REST API:
   ```
   POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_WEB_API_KEY
   Body: {"email": "test@institute.edu", "password": "testpass123", "returnSecureToken": true}
   ```
   The response contains `idToken` — this is your Bearer token.
3. **Test in Swagger UI**: Click the 🔒 Authorize button, paste the token
4. Hit `GET /api/v1/auth/me` — should return `401` before registration, then the user profile after `POST /register`
5. **Token expiry test**: Wait 60+ minutes (or set your clock forward), re-send the same token — confirm `401 Unauthorized` with a clear "token expired" message
6. **Garbage token test**: Send `Authorization: Bearer totallynotavalidtoken` — confirm a structured error, not a stack trace
7. **Database verification**: `psql` into the database and `SELECT * FROM users;` — confirm the row matches what the API returned

### Conceptual Pitfalls

> [!CAUTION]
> **Do NOT manually verify JWTs with `python-jose`**. Your TAD shows a manual JWK fetch + decode flow. While that's educationally correct, `firebase_admin.auth.verify_id_token()` does all of this internally with proper caching, clock skew tolerance, and revocation checks. Rolling your own means you'll miss edge cases like token revocation. Use the Admin SDK method.

> [!WARNING]
> **The "register before profile exists" gap**: When a user first authenticates via Firebase Auth, they exist in Auth but NOT in PostgreSQL. Your `get_current_user` dependency must handle this gracefully — either return a "partial" user context (authenticated but unregistered) or force a registration redirect. Design this state machine explicitly. Consider having two auth dependencies:
> - `verify_firebase_token` — just verifies the JWT, returns claims (used by `/register`)
> - `get_current_user` — verifies JWT AND fetches DB profile (used by all other routes)

- **Token refresh is a client concern**: The backend should *never* refresh tokens. It only validates them. The React client will handle `onIdTokenChanged` listeners. Your backend sees every request as stateless and independent.
- **Custom claims propagation delay**: When you set custom claims (like `role`) via the Admin SDK, they don't appear in the user's *current* token. The user must re-authenticate or force a token refresh. This matters for your testing workflow — after setting claims, re-call the sign-in REST API to get a fresh token.
- **`email_verified` gating**: Decide now whether unverified emails can access any routes. If yes, annotate it. If no, add the check inside `verify_firebase_token`. Don't leave it ambiguous.

---

## Milestone 3 — RBAC Enforcement Layer

### Core Objective
Build a flexible, reusable role-gating system using Firebase Custom Claims and FastAPI dependencies. By the end, you should be able to lock any route to `STUDENT`, `CR`, or `ADMIN` with a one-liner.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/core/rbac.py` — Role enforcement module:
  - Define a `Role` enum (Python `enum.IntEnum` for hierarchy comparison):
    ```
    STUDENT = 1
    CR = 2
    ADMIN = 3
    ```
  - Implement a `RoleChecker` callable class:
    - Constructor accepts `minimum_role: Role`
    - `__call__` method takes the decoded token, extracts the `role` claim, compares against the hierarchy using integer comparison (`user_level >= required_level`)
    - Returns the token payload if authorized, raises `403` otherwise
  - Implement helper dependency instances:
    - `require_student = RoleChecker(Role.STUDENT)`
    - `require_cr = RoleChecker(Role.CR)`
    - `require_admin = RoleChecker(Role.ADMIN)`
- [ ] `app/core/claims.py` — Admin SDK custom claims management:
  - `set_user_role(uid: str, role: Role)` — calls `auth.set_custom_user_claims(uid, {"role": role.value})`
  - `get_user_claims(uid: str)` — retrieves current custom claims for a user
- [ ] `app/api/v1/admin.py` — Admin management endpoints:
  - `POST /api/v1/admin/users/{uid}/role` — Sets a user's role (Admin-only)
  - `GET /api/v1/admin/users/pending` — Lists users with `approval_status = PENDING`
  - `POST /api/v1/admin/users/{uid}/approve` — Approves a pending user registration
- [ ] Update `POST /api/v1/auth/register` to set `approval_status = PENDING` by default
- [ ] Add PostgreSQL enum types via Alembic migration:
  ```python
  # In your ORM model file, define native PG enums
  import enum
  class RoleEnum(str, enum.Enum):
      STUDENT = "STUDENT"
      CR = "CR"
      ADMIN = "ADMIN"
  ```

#### Dual-Source Role Truth

> [!IMPORTANT]
> With PostgreSQL replacing Firestore, your user's role lives in **two places**:
> 1. **Firebase Custom Claims** (inside the JWT) — used for fast request-level RBAC without a DB hit
> 2. **PostgreSQL `users.role` column** — the authoritative source of truth
>
> When an Admin changes a user's role, you must update BOTH:
> 1. `UPDATE users SET role = 'CR' WHERE id = ...` (PostgreSQL)
> 2. `auth.set_custom_user_claims(uid, {"role": "CR"})` (Firebase)
>
> If they ever diverge, PostgreSQL wins. Consider adding a background reconciliation check.

### Testing & Verification
1. Create three test users in Firebase Auth (one per role)
2. Use the admin endpoint or a seed script to set custom claims:
   - User A: `{"role": "STUDENT"}`
   - User B: `{"role": "CR"}`
   - User C: `{"role": "ADMIN"}`
3. Re-authenticate all three via the REST API to get fresh tokens with claims baked in
4. Test matrix — for each protected endpoint, verify:

| Endpoint | STUDENT | CR | ADMIN |
|---|---|---|---|
| `GET /api/v1/auth/me` | ✅ 200 | ✅ 200 | ✅ 200 |
| `POST /api/v1/announcements` | ❌ 403 | ✅ 202 | ✅ 202 |
| `POST /api/v1/admin/users/{uid}/role` | ❌ 403 | ❌ 403 | ✅ 200 |
| `DELETE /api/v1/resources/{id}` | ❌ 403 | ❌ 403 | ✅ 200 |

5. Test with a token that has *no* `role` claim — confirm it defaults to `STUDENT` level, not a crash

### Conceptual Pitfalls

> [!WARNING]
> **Claims size limit**: Firebase custom claims payload is capped at **1000 bytes**. Only store the role string. Everything else lives in PostgreSQL.

- **Stale claims in active tokens**: Custom claims are baked into the JWT at issuance time. If you promote a user from STUDENT to CR, their *existing* token still says STUDENT until they refresh. Tokens expire in 1 hour — accept this delay. Document it as known behavior.
- **Don't conflate `approval_status` with `role`**: A user can be `APPROVED` with role `STUDENT`. These are orthogonal axes. A `PENDING` user should be blocked at the auth middleware level, before RBAC even runs. Layer the checks: Auth → Approval Check → RBAC.
- **Self-escalation prevention**: Ensure the "set role" endpoint validates that only Admins can call it, AND that an Admin cannot demote themselves (which would lock everyone out if there's only one admin).

---

## Milestone 4 — User Management & Student Directory

### Core Objective
Build the complete user lifecycle: registration, profile management, directory listing with filtering, and the admin approval queue. This is the first full vertical slice through all layers (route → service → repository → PostgreSQL).

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/repositories/user_repository.py`:
  - `create(session, data)` — Insert new user row
  - `get_by_firebase_uid(session, firebase_uid)` — For auth dependency
  - `get_by_id(session, user_id)` — By PostgreSQL UUID
  - `get_by_roll_number(session, roll_number)` — For uniqueness validation
  - `get_users_by_batch(session, batch_id, limit, offset)` — Paginated directory query
  - `get_pending_users(session)` — Filter by `approval_status = 'PENDING'`
  - `update(session, user_id, data)` — Partial update
  - `count_by_batch(session, batch_id)` — For pagination metadata
- [ ] `app/services/user_service.py`:
  - Orchestrates registration: validate roll number uniqueness → create row → set initial Firebase claims
  - Orchestrates approval: update status → set custom claims if needed
  - Orchestrates profile update: validate ownership → update row
- [ ] `app/schemas/user.py` — Expand with:
  - `UserCreate`: `name`, `roll_number`, `batch_id`, `profile_photo_url` (optional)
  - `UserUpdate`: All fields optional (partial update pattern)
  - `UserResponse`: Public fields only (no `approval_status` for non-admins)
  - `UserListResponse`: Paginated wrapper with `items`, `total`, `page`, `per_page`
- [ ] `app/api/v1/users.py` — User endpoints:
  - `GET /api/v1/users/directory` — Paginated, filterable by `batch_id`
  - `GET /api/v1/users/{user_id}` — Single user profile
  - `PATCH /api/v1/users/{user_id}` — Update own profile
  - `GET /api/v1/users/directory/search?q=` — Search by name or roll number

#### PostgreSQL Pagination — Simple and Proper

> [!TIP]
> Unlike Firestore's cursor-based-only pagination, PostgreSQL gives you real `LIMIT`/`OFFSET`:
> ```sql
> SELECT * FROM users
> WHERE batch_id = 1
> ORDER BY name ASC
> LIMIT 10 OFFSET 20;
> ```
> Your repository method takes `limit` and `offset` as parameters. Your service layer converts the frontend's `page` + `per_page` into `offset = (page - 1) * per_page`. Return `total` via a `SELECT COUNT(*)` query so the frontend can render page numbers.

#### Roll Number Uniqueness — The PostgreSQL Way

In Firestore, you'd need a query-then-write transaction to prevent duplicates. In PostgreSQL:
```sql
-- In your migration / ORM model
roll_number VARCHAR UNIQUE NOT NULL
```
That's it. The database enforces it. Your repository catches the `IntegrityError` and converts it to a `409 Conflict` HTTP response.

### Testing & Verification
1. Register a new user via `POST /api/v1/auth/register` with a valid token — confirm `approval_status` is `PENDING`
2. As Admin, hit `GET /api/v1/admin/users/pending` — confirm the new user appears
3. Approve the user via `POST /api/v1/admin/users/{uid}/approve` — confirm status flips to `APPROVED`
4. Hit `GET /api/v1/users/directory?batch_id=1&page=1&per_page=10` — confirm the approved user shows up
5. Try `PATCH /api/v1/users/{other_user_id}` as a non-admin — confirm `403`
6. Try `PATCH /api/v1/users/{own_user_id}` — confirm success
7. Try to register with a duplicate `roll_number` — confirm `409 Conflict`
8. Test pagination: Seed 25+ users, request `?page=1&per_page=10`, verify `total=25`, `items` has 10 entries
9. Verify in psql: `SELECT COUNT(*) FROM users WHERE batch_id = 1;` — should match API response

### Conceptual Pitfalls

> [!WARNING]
> **SQLAlchemy `IntegrityError` handling**: When a unique constraint is violated, SQLAlchemy raises `IntegrityError`. You need to catch this at the repository or service layer and convert it to an appropriate HTTP error. Don't let raw database exceptions propagate to the API consumer — they leak schema details.

- **Partial updates with Pydantic**: Use `model.model_dump(exclude_unset=True)` to get only the fields the client actually sent. Don't overwrite existing values with `None` just because the client didn't include a field. This is a subtle but critical distinction between "field is `None`" and "field was not sent."
- **Profile photo URL validation**: Don't trust client-submitted URLs. If you allow arbitrary URLs for `profile_photo_url`, validate the domain (must be your Firebase Storage bucket). Better yet, only accept URLs that match your storage path convention.
- **Search with `ILIKE`**: PostgreSQL's `WHERE name ILIKE '%query%'` works perfectly for your scale (<500 users). For larger datasets, you'd use `tsvector` full-text search, but `ILIKE` is fine here and much simpler.

---

## Milestone 5 — Announcements Module

### Core Objective
Build the announcements CRUD with RBAC-gated creation (CR + Admin only), batch-scoped and global announcement queries, and PostgreSQL persistence. This milestone is **synchronous only** — the Redis/WhatsApp async pipeline comes in Milestone 8.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/db/models/announcement.py`:
  ```python
  # Conceptual shape
  class Announcement(Base):
      __tablename__ = "announcements"
      id: Mapped[uuid.UUID]
      title: Mapped[str]
      content: Mapped[str]           # Text column for longer content
      author_id: Mapped[uuid.UUID]   # FK → users.id
      batch_id: Mapped[Optional[int]] # FK → batches.id, nullable (null = global)
      created_at: Mapped[datetime]
      updated_at: Mapped[datetime]
      # Relationships
      author: Mapped["User"] = relationship(...)
      batch: Mapped[Optional["Batch"]] = relationship(...)
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "create_announcements_table"`
- [ ] `app/repositories/announcement_repository.py`:
  - `create(session, data)` — Insert new row
  - `get_by_id(session, announcement_id)` — Single announcement with author joined
  - `get_feed(session, batch_id, limit, offset)` — **The key query**: batch-specific + global, sorted by `created_at DESC`
  - `delete(session, announcement_id)` — Admin only
  - `count_feed(session, batch_id)` — For pagination
- [ ] `app/services/announcement_service.py`:
  - Create: Validate author has CR/Admin role → persist to PostgreSQL → (placeholder for async dispatch)
  - Feed: Single query using SQL `OR`
- [ ] `app/schemas/announcement.py`:
  - `AnnouncementCreate`: `title`, `content`, `batch_id` (optional — null = global)
  - `AnnouncementResponse`: Full response with embedded author info
- [ ] `app/api/v1/announcements.py`:
  - `POST /api/v1/announcements` — CR/Admin only
  - `GET /api/v1/announcements?batch_id=1&page=1&per_page=20` — Feed endpoint
  - `GET /api/v1/announcements/{id}` — Single announcement
  - `DELETE /api/v1/announcements/{id}` — Admin only

#### The Feed Query — PostgreSQL Shines Here

> [!TIP]
> The "show me global announcements AND batch-specific ones" query that required two separate Firestore queries + Python merge is a single SQL statement:
> ```sql
> SELECT a.*, u.name as author_name, u.role as author_role
> FROM announcements a
> JOIN users u ON a.author_id = u.id
> WHERE a.batch_id = :target_batch OR a.batch_id IS NULL
> ORDER BY a.created_at DESC
> LIMIT :limit OFFSET :offset;
> ```
> One query. Properly sorted. With the author's name joined in. No denormalization needed.

### Testing & Verification
1. As CR: `POST /api/v1/announcements` with `batch_id = 1` — should succeed
2. As CR: `POST /api/v1/announcements` without `batch_id` — should create a global announcement
3. As STUDENT: `POST /api/v1/announcements` — should return `403`
4. `GET /api/v1/announcements?batch_id=1` — should return batch_1 announcements + global ones, mixed and sorted by date
5. `GET /api/v1/announcements?batch_id=2` — should NOT return batch_1 announcements, but SHOULD return globals
6. As Admin: `DELETE /api/v1/announcements/{id}` — should succeed
7. As CR: `DELETE /api/v1/announcements/{id}` — should return `403`
8. Verify in psql: `SELECT * FROM announcements ORDER BY created_at DESC;`

### Conceptual Pitfalls

- **Author deletion cascade**: Decide what happens when a user is deleted. Options:
  - `ON DELETE CASCADE` — all their announcements disappear. Probably not what you want.
  - `ON DELETE SET NULL` — `author_id` becomes null. You display "Deleted User."
  - `ON DELETE RESTRICT` — prevent user deletion if they have announcements. Safest but can be annoying.
  
  Set this in your foreign key definition. **Decide now**, changing it later requires a migration.
- **SQLAlchemy relationship loading**: When you load an announcement, SQLAlchemy can load the `author` relationship via:
  - `lazy="select"` — N+1 query problem if you load 20 announcements (20 extra queries for authors)
  - `selectinload(Announcement.author)` — Explicit eager load in the query. **Use this.**
  - `joinedload(Announcement.author)` — LEFT JOIN in the same query. Also good.
  
  Choose `selectinload` or `joinedload` explicitly in your repository queries. Never rely on lazy loading in an async context — it doesn't work with `AsyncSession` by default.

> [!CAUTION]
> **Lazy loading is disabled by default with `AsyncSession`**. If you access `announcement.author` without eager loading it in the query, SQLAlchemy will raise `MissingGreenlet` error. You MUST use explicit loading strategies (`joinedload`, `selectinload`) in every query that needs related objects. This is not optional — it's an async SQLAlchemy requirement.

---

## Milestone 6 — The Vault: Resource Management & Cloud Storage

### Core Objective
Build the academic resource lifecycle: intent validation, direct-to-Storage upload (client-side), metadata registration in PostgreSQL, admin approval queue, and browseable catalogue with filtering by batch/semester/subject/material type.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/db/models/resource.py`:
  ```python
  # Conceptual shape
  class VaultResource(Base):
      __tablename__ = "vault_resources"
      id: Mapped[uuid.UUID]
      uploader_id: Mapped[uuid.UUID]     # FK → users.id
      batch_id: Mapped[int]              # FK → batches.id
      semester: Mapped[int]
      subject: Mapped[str]
      material_type: Mapped[MaterialTypeEnum]  # PG ENUM: PYQ, NOTES, LAB, OTHER
      file_url: Mapped[str]
      approval_status: Mapped[ApprovalStatusEnum]  # Default PENDING
      created_at: Mapped[datetime]
      # Relationships
      uploader: Mapped["User"] = relationship(...)
      batch: Mapped["Batch"] = relationship(...)
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "create_vault_resources_table"`
- [ ] `app/repositories/resource_repository.py`:
  - `create(session, data)` — With `approval_status = PENDING`
  - `get_approved(session, batch_id, semester, subject, material_type, limit, offset)` — Multi-filter catalogue query
  - `get_pending(session)` — Admin approval queue
  - `get_by_id(session, resource_id)`
  - `update_status(session, resource_id, status)`
  - `delete(session, resource_id)`
- [ ] `app/services/resource_service.py`:
  - **Validate intent**: Check file extension against allowlist, enforce size limit
  - **Generate signed upload URL**: Use `google-cloud-storage` library to generate a V4 signed URL for direct client upload
  - **Register metadata**: After client upload, verify object exists in Storage, then insert PostgreSQL row
  - **Approve/Reject**: Admin workflow — update `approval_status`
  - **Delete**: Delete PostgreSQL row + Cloud Storage object
- [ ] `app/schemas/resource.py`:
  - `ResourceIntentRequest`: `file_name`, `file_size_bytes`, `content_type`
  - `ResourceIntentResponse`: `upload_url`, `upload_path`, `expires_at`
  - `ResourceRegister`: `upload_path`, `semester`, `subject`, `material_type`, `batch_id`
  - `ResourceResponse`: Full metadata
- [ ] `app/api/v1/resources.py`:
  - `POST /api/v1/resources/validate-intent` — Policy check + signed URL generation
  - `POST /api/v1/resources/register` — Post-upload metadata registration
  - `GET /api/v1/resources?batch_id=1&semester=3&subject=VLSI&type=PYQ` — Filterable catalogue (approved only for students)
  - `GET /api/v1/resources/pending` — Admin approval queue
  - `POST /api/v1/resources/{id}/approve` — Admin
  - `POST /api/v1/resources/{id}/reject` — Admin
  - `DELETE /api/v1/resources/{id}` — Admin (cascades to Storage)

#### Multi-Filter Catalogue Query

> [!TIP]
> PostgreSQL handles multi-filter queries elegantly. Build the query dynamically in your repository:
> ```python
> # Conceptual approach — build WHERE clause conditionally
> query = select(VaultResource).where(VaultResource.approval_status == "APPROVED")
> if batch_id:
>     query = query.where(VaultResource.batch_id == batch_id)
> if semester:
>     query = query.where(VaultResource.semester == semester)
> if subject:
>     query = query.where(VaultResource.subject == subject)
> if material_type:
>     query = query.where(VaultResource.material_type == material_type)
> query = query.order_by(VaultResource.created_at.desc()).limit(limit).offset(offset)
> ```
> This composable query pattern is one of SQLAlchemy's greatest strengths.

#### Cloud Storage Path Convention
```
gs://your-bucket/
├── academic-materials/
│   └── {batch_id}/
│       └── sem_{semester}/
│           └── {subject}/
│               └── {material_type}/
│                   └── {uuid}_{original_filename}
└── gallery-media/
    └── {event_id}/
        └── {uuid}_{original_filename}
```

#### Firebase Cloud Storage Security Rules (still applies)

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    function isAuthenticated() {
      return request.auth != null;
    }
    function getUserRole() {
      return request.auth.token.role;
    }
    match /academic-materials/{allPaths=**} {
      allow read: if isAuthenticated();
      allow write: if isAuthenticated()
                   && request.resource.size < 50 * 1024 * 1024
                   && request.resource.contentType.matches('application/pdf|application/zip');
    }
    match /gallery-media/{allPaths=**} {
      allow read: if isAuthenticated();
      allow write: if isAuthenticated()
                   && request.resource.size < 10 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*');
    }
  }
}
```

### Testing & Verification

Testing file uploads without a frontend requires a two-step simulation:

1. **Intent validation**: `POST /api/v1/resources/validate-intent` with valid file metadata → should return a signed URL
2. **Simulate upload**: Use `curl` or Postman to PUT a file to the signed URL:
   ```bash
   curl -X PUT -H "Content-Type: application/pdf" --upload-file test.pdf "SIGNED_URL_HERE"
   ```
3. **Register metadata**: `POST /api/v1/resources/register` with the upload path → should create a `PENDING` resource
4. **Admin queue**: `GET /api/v1/resources/pending` as Admin → should show the resource
5. **Approve**: `POST /api/v1/resources/{id}/approve` → status should flip
6. **Catalogue**: `GET /api/v1/resources?batch_id=1&semester=3&subject=VLSI` → should show approved resources
7. **Size limit test**: Submit an intent for a 100MB file → should get `400` rejection
8. **Invalid type test**: Submit intent for a `.exe` file → should get `400` rejection
9. **Verify in psql**: `SELECT * FROM vault_resources WHERE approval_status = 'APPROVED';`

### Conceptual Pitfalls

> [!CAUTION]
> **Signed URL expiry window**: Make signed upload URLs short-lived (15 minutes max). If a URL leaks, an attacker can only upload within that window.

> [!WARNING]
> **Metadata registration without upload verification**: The client claims it uploaded successfully and sends you a `register` request. But did the file actually land in Storage? **Always verify** by checking `bucket.blob(path).exists()` before writing to PostgreSQL. Otherwise, you get orphaned metadata pointing to non-existent files.

- **Storage deletion cascade**: When an admin deletes a resource, you must delete BOTH the PostgreSQL row AND the Cloud Storage object. If your Storage delete fails after the DB delete succeeds, you have an orphan blob. Handle this gracefully — log the failure, don't silently swallow it.
- **Duplicate uploads**: Two students uploading the same file name will collide. The UUID prefix (`{uuid}_{original_filename}`) prevents this.
- **Composite index**: If you frequently query by `(batch_id, semester, subject, material_type)`, add a composite index in a migration. PostgreSQL won't auto-create it — but it will tell you about slow queries via `EXPLAIN ANALYZE`.

---

## Milestone 7 — The Chronicles: Events, Timeline & Gallery

### Core Objective
Build the event/timeline data model with event-media relationships, supporting chronological queries by batch and event-detail → media-gallery drill-down.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/db/models/event.py`:
  ```python
  # Conceptual shape
  class Event(Base):
      __tablename__ = "events"
      id: Mapped[uuid.UUID]
      title: Mapped[str]
      description: Mapped[Optional[str]]
      event_date: Mapped[date]
      batch_id: Mapped[Optional[int]]   # FK → batches.id, nullable (null = global)
      created_at: Mapped[datetime]
      # Relationships
      media: Mapped[list["EventMedia"]] = relationship(back_populates="event", cascade="all, delete-orphan")

  class EventMedia(Base):
      __tablename__ = "event_media"
      id: Mapped[uuid.UUID]
      event_id: Mapped[uuid.UUID]       # FK → events.id, ON DELETE CASCADE
      media_url: Mapped[str]
      media_type: Mapped[str]           # e.g., "image/jpeg", "video/mp4"
      created_at: Mapped[datetime]
      # Relationships
      event: Mapped["Event"] = relationship(back_populates="media")
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "create_events_and_media_tables"`
- [ ] `app/repositories/event_repository.py`:
  - `create_event(session, data)` — CR/Admin only
  - `get_events_by_batch(session, batch_id, limit, offset)` — Sorted by `event_date DESC`, includes media count
  - `get_event_with_media(session, event_id)` — Single event with all media eagerly loaded
  - `update_event(session, event_id, data)`
  - `delete_event(session, event_id)` — **CASCADE handles media rows automatically**
- [ ] `app/repositories/event_media_repository.py`:
  - `add_media(session, event_id, media_data)`
  - `get_media_by_event(session, event_id)`
  - `delete_media(session, media_id)` — Also delete Storage object
- [ ] `app/services/event_service.py`:
  - Event CRUD orchestration
  - Media management with Storage cleanup on delete
- [ ] `app/schemas/event.py`:
  - `EventCreate`: `title`, `description`, `event_date`, `batch_id` (optional)
  - `EventResponse`: Event data + `media_count` (avoid loading all URLs in list views)
  - `EventDetailResponse`: Event data + full `media` array
  - `MediaCreate`: `media_url`, `media_type`
  - `MediaResponse`: Full media metadata
- [ ] `app/api/v1/events.py`:
  - `POST /api/v1/events` — CR/Admin
  - `GET /api/v1/events?batch_id=1` — Timeline listing with media count
  - `GET /api/v1/events/{id}` — Event detail with full media
  - `POST /api/v1/events/{id}/media` — Add media (signed URL pattern, same as Vault)
  - `DELETE /api/v1/events/{id}` — Admin only (cascades to media rows)
  - `DELETE /api/v1/events/{id}/media/{media_id}` — Admin only

#### CASCADE Deletes — PostgreSQL Handles This

> [!TIP]
> Unlike Firestore (where you had to manually enumerate and delete subcollection documents), PostgreSQL handles cascade deletes via the foreign key constraint:
> ```python
> event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
> ```
> When you delete an event, all its `event_media` rows are automatically deleted by the database. You also want `cascade="all, delete-orphan"` on the SQLAlchemy relationship for ORM-level cascade awareness.

#### Media Count Without Full Load

```sql
-- In your timeline listing query, use a subquery for count
SELECT e.*, (SELECT COUNT(*) FROM event_media em WHERE em.event_id = e.id) as media_count
FROM events e
WHERE e.batch_id = :batch_id OR e.batch_id IS NULL
ORDER BY e.event_date DESC;
```

Or use SQLAlchemy's `func.count()` with a subquery or `selectinload` + Python `len()` for simplicity at your scale.

### Testing & Verification
1. Create an event with a past date → verify it appears in timeline query sorted correctly
2. Create a global event (no `batch_id`) → verify it appears for all batch queries
3. Add 3 media items to an event → `GET /api/v1/events/{id}` should return all 3 with full URLs
4. **Delete an event** → verify the `event_media` rows are **automatically deleted** (check psql: `SELECT * FROM event_media WHERE event_id = 'deleted-id'` — should be empty)
5. Verify timeline ordering: create events with dates in 2023, 2025, 2024 → query returns 2025, 2024, 2023
6. Verify `media_count` in list view: should show `3` without loading all media URLs

### Conceptual Pitfalls

- **Storage blobs are NOT cascade-deleted**: The PostgreSQL `CASCADE` deletes the `event_media` rows, but the actual files in Firebase Cloud Storage are still there. You need application-level cleanup: before deleting an event, query all its media URLs, then delete the Storage blobs, then delete the event. Or: accept orphan blobs and run a periodic cleanup job.
- **Date vs. Datetime**: `event_date` is a `date` type (no time component). `created_at` is a `datetime`. Don't mix them up in your ORM model — SQLAlchemy distinguishes `Date` from `DateTime`.
- **Composite index**: Add an index on `(batch_id, event_date)` for the timeline query. This is a single migration:
  ```python
  Index("ix_events_batch_date", "batch_id", "event_date")
  ```

---

## Milestone 8 — Redis Integration & Async Worker Pipeline

### Core Objective
Stand up a Redis message broker, build the producer-consumer pipeline, and demonstrate end-to-end async task execution. Wire the announcement creation flow to an async dispatch queue — the WhatsApp webhook is mocked at this stage.

### System Design Checklist

#### Files to Create/Modify
- [ ] `app/core/redis.py` — Redis connection management:
  - Use `redis.asyncio` (formerly `aioredis`) for non-blocking Redis operations
  - Initialize connection pool in the `lifespan` context manager
  - Expose `get_redis()` dependency for injection into routes/services
- [ ] `app/config.py` — Add settings:
  - `REDIS_URL`: Default `redis://localhost:6379/0`
  - `ANNOUNCEMENT_QUEUE_KEY`: `"queue:announcements"`
  - `TASK_RESULT_TTL`: How long to keep task results (e.g., 86400 seconds)
- [ ] `app/services/queue_service.py` — Producer side:
  - `enqueue_announcement(redis, announcement_data)`:
    - Generate a task UUID
    - Serialize the payload to JSON
    - `RPUSH` to the announcements queue
    - Return the task UUID to the caller
  - `get_task_status(redis, task_id)` — Check if a task has been processed (lookup in a results hash)
- [ ] `app/workers/announcement_worker.py` — Consumer side:
  - Runs as a separate process (`python -m app.workers.announcement_worker`)
  - Has its **own** PostgreSQL session factory and Redis connection (NOT shared with FastAPI)
  - Event loop: `BLPOP queue:announcements 0` (blocking pop, infinite wait)
  - On receiving a message:
    1. Deserialize JSON payload
    2. Execute the task (for now: log it + sleep 2s to simulate webhook call)
    3. Write result to `HSET task_results:{task_id}` with status and timestamp
    4. Optionally update the announcement row in PostgreSQL with a `webhook_status` field
  - Implement graceful shutdown on `SIGTERM`/`SIGINT`
- [ ] Update `app/services/announcement_service.py`:
  - After persisting the announcement to PostgreSQL, call `enqueue_announcement()` to push the webhook task
- [ ] Update `POST /api/v1/announcements` response:
  - Return `HTTP 202 Accepted` with `{"announcement_id": "...", "task_id": "...", "status": "queued"}`
- [ ] `GET /api/v1/tasks/{task_id}/status` — Optional polling endpoint

#### Architecture Decision: Celery vs. Raw Redis

> [!IMPORTANT]
> For your scale (a university branch — maybe 10 announcements per week), a raw Redis consumer loop is simpler and more educational than Celery. You'll learn what Celery abstracts away by building the queue consumer yourself. You can always migrate to Celery/Arq later if you need retry policies, rate limiting, or scheduled tasks.

#### Worker Database Access

> [!WARNING]
> The worker process needs its own SQLAlchemy engine and session factory. It does NOT share the FastAPI application's engine. Create a standalone `create_async_engine()` inside the worker's initialization code. Same `DATABASE_URL`, separate connection pool.

#### Retry & Dead-Letter Pattern
```
queue:announcements          → Primary work queue
queue:announcements:retry    → Failed tasks waiting for retry
queue:announcements:dead     → Tasks that exceeded max retries (manual intervention needed)
```

### Testing & Verification
1. **Start Redis locally**: `docker run -d --name ee-vlsi-redis -p 6379:6379 redis:7-alpine`
2. **Start the API server** in one terminal
3. **Start the worker** in a second terminal: `python -m app.workers.announcement_worker`
4. **Post an announcement** as CR via Swagger UI
5. Observe:
   - API returns `202` immediately with a `task_id`
   - Worker terminal logs receipt and processing of the task
   - Redis queue should be empty after processing (`redis-cli LLEN queue:announcements` → 0)
6. **Check task status**: `GET /api/v1/tasks/{task_id}/status` should show `completed`
7. **Kill the worker**, post another announcement, verify it sits in the queue (`LLEN` → 1), then restart the worker — it should pick up the queued task
8. **Simulate failure**: Make the worker throw an exception during processing → verify the task goes to the retry queue, not silently dropped

### Conceptual Pitfalls

> [!CAUTION]
> **At-least-once vs. exactly-once delivery**: `BLPOP` removes the item from the queue the moment it's read. If your worker crashes *after* reading but *before* processing, the task is lost. To prevent this, use `BRPOPLPUSH` (or `BLMOVE`): atomically move the item to a "processing" list, then delete from "processing" only after successful execution. This gives you at-least-once semantics.

- **Worker and API are separate processes**: The worker does NOT run inside FastAPI. They share the same codebase but have independent lifecycles. Don't import FastAPI request context inside the worker.
- **JSON serialization boundaries**: Everything going into Redis must be JSON-serialized. Use Pydantic's `.model_dump_json()` for serialization and `Model.model_validate_json()` for deserialization. Don't use `pickle`.
- **Graceful shutdown**: The `BLPOP` call blocks indefinitely. When you hit `Ctrl+C`, use Python's `signal` module to catch `SIGTERM` and set a shutdown flag that breaks the loop.
- **Redis memory limits**: Set a `maxmemory` policy. For your scale this is unlikely to matter, but add a `LLEN` health check anyway.

---

## Milestone 9 — Hall of Fame, Forge & Remaining Modules

### Core Objective
Complete the remaining domain modules: Hall of Fame (superlatives) and Forge (projects/toolkits). These follow the same repository → service → route pattern you've now established. This milestone should go fast.

### System Design Checklist

#### Hall of Fame
- [ ] `app/db/models/hall_of_fame.py`:
  ```python
  class HallOfFame(Base):
      __tablename__ = "hall_of_fame"
      id: Mapped[uuid.UUID]
      user_id: Mapped[uuid.UUID]    # FK → users.id
      batch_id: Mapped[int]         # FK → batches.id
      title: Mapped[str]            # "Topper", "Best Comedian", "Eminence in Shadow"
      awarded_at: Mapped[datetime]
      # Relationships
      user: Mapped["User"] = relationship(...)
      batch: Mapped["Batch"] = relationship(...)
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "create_hall_of_fame_table"`
- [ ] `app/repositories/hall_of_fame_repository.py`:
  - `create_award(session, data)` — Admin only
  - `get_awards_by_batch(session, batch_id)` — Returns all superlatives for a batch, with user info JOINed
  - `delete_award(session, award_id)` — Admin only
- [ ] `app/api/v1/hall_of_fame.py`:
  - `POST /api/v1/hall-of-fame` — Admin only
  - `GET /api/v1/hall-of-fame?batch_id=1` — List by batch (JOINed with user names and photos)
  - `DELETE /api/v1/hall-of-fame/{id}` — Admin only
- [ ] `app/schemas/hall_of_fame.py`:
  - `AwardCreate`: `user_id`, `batch_id`, `title`
  - `AwardResponse`: Award data + user name + user photo (via JOIN, not denormalization)

> [!TIP]
> With PostgreSQL, the award response includes live user data via JOIN — if a user updates their profile photo, the Hall of Fame automatically reflects it. No stale denormalized snapshots. If you *want* a historical snapshot (photo at time of award), store it explicitly as `snapshot_photo_url`. But that's a product decision, not a technical constraint.

#### The Forge: Projects
- [ ] `app/db/models/project.py`:
  ```python
  class Project(Base):
      __tablename__ = "projects"
      id: Mapped[uuid.UUID]
      title: Mapped[str]
      description: Mapped[Optional[str]]
      tech_stack: Mapped[list[str]]     # PostgreSQL ARRAY type
      repo_url: Mapped[Optional[str]]
      author_id: Mapped[uuid.UUID]      # FK → users.id
      created_at: Mapped[datetime]
      updated_at: Mapped[datetime]
      # Relationships
      author: Mapped["User"] = relationship(...)
  ```
- [ ] Generate migration: `alembic revision --autogenerate -m "create_projects_table"`
- [ ] `app/repositories/project_repository.py`:
  - `create(session, data)` — Any authenticated user
  - `get_all(session, limit, offset)` — Paginated listing with author JOINed
  - `get_by_author(session, author_id)`
  - `get_by_id(session, project_id)`
  - `update(session, project_id, data)` — Author or Admin
  - `delete(session, project_id)` — Author or Admin
- [ ] `app/api/v1/projects.py`:
  - `POST /api/v1/projects`
  - `GET /api/v1/projects`
  - `GET /api/v1/projects/{id}`
  - `PATCH /api/v1/projects/{id}`
  - `DELETE /api/v1/projects/{id}`
- [ ] `app/schemas/project.py`:
  - `ProjectCreate`: `title`, `description`, `tech_stack` (list of strings), `repo_url`
  - `ProjectResponse`: Full project data with author info

#### `tech_stack` as PostgreSQL ARRAY

> [!TIP]
> PostgreSQL supports native `ARRAY` columns. Store `tech_stack` as `ARRAY(String)`:
> ```python
> from sqlalchemy.dialects.postgresql import ARRAY
> tech_stack: Mapped[list[str]] = mapped_column(ARRAY(String))
> ```
> This enables queries like "find all projects using Python":
> ```sql
> SELECT * FROM projects WHERE 'Python' = ANY(tech_stack);
> ```
> In SQLAlchemy: `.where(Project.tech_stack.any("Python"))`. Far better than comma-separated strings.

#### Ownership Authorization — Reusable Pattern

> [!IMPORTANT]
> Both Projects and Profile Updates need an **ownership check**: the requesting user must be either the resource owner OR an Admin. Extract this into a reusable service utility:
> ```python
> def verify_ownership(resource_owner_id: uuid.UUID, current_user: CurrentUser):
>     if current_user.id != resource_owner_id and current_user.role != Role.ADMIN:
>         raise HTTPException(403, "Not authorized to modify this resource")
> ```
> Don't duplicate this logic in every route handler.

### Testing & Verification
1. Create awards for multiple users in the same batch → `GET /api/v1/hall-of-fame?batch_id=1` returns all with user details
2. Verify non-admin cannot create awards → `403`
3. Create a project as Student → verify it appears in listing with author info
4. Try to edit another user's project as Student → `403`
5. Edit another user's project as Admin → `200`
6. Delete a project as its author → verify it's gone from listing
7. Filter projects by tech: `GET /api/v1/projects?tech=Python` → only matching projects
8. Verify in psql: JOINs work correctly — `SELECT h.*, u.name FROM hall_of_fame h JOIN users u ON h.user_id = u.id;`

### Conceptual Pitfalls
- **Hall of Fame uniqueness**: Can a user have multiple titles in the same batch? Can two users share the same title? If not, add a composite unique constraint: `UniqueConstraint("user_id", "batch_id", "title")`. PostgreSQL enforces this for you.
- **Relationship loading in lists**: When loading a list of projects with authors, use `selectinload(Project.author)` to avoid N+1 queries. This matters even at small scale — it's a good habit.

---

## Milestone 10 — WhatsApp Webhook, Containerization & Final Integration

### Core Objective
Replace the mock webhook call in your worker with the real WhatsApp API integration, Dockerize the entire stack (API + Worker + PostgreSQL + Redis), and perform end-to-end integration testing across all modules.

### System Design Checklist

#### WhatsApp Webhook Integration
- [ ] `app/workers/webhook_dispatcher.py`:
  - Implement the actual HTTP POST to the WhatsApp webhook endpoint using `httpx` (async)
  - Structure the payload per the webhook API spec
  - Implement retry logic: 3 retries with exponential backoff (1s, 4s, 16s)
  - On max retries exceeded: move to dead-letter queue + log failure
- [ ] `app/config.py` — Add:
  - `WHATSAPP_WEBHOOK_URL`
  - `WHATSAPP_API_TOKEN` (as `SecretStr`)
  - `WEBHOOK_MAX_RETRIES`: Default 3
  - `WEBHOOK_BASE_DELAY_SECONDS`: Default 1

#### Containerization
- [ ] `Dockerfile`:
  - Multi-stage build: builder stage for dependencies, slim runtime stage
  - Non-root user execution
  - Health check endpoint wired to `GET /api/v1/health`
  - Separate entrypoint for API vs. Worker (same image, different `CMD`):
    - API: `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
    - Worker: `CMD ["python", "-m", "app.workers.announcement_worker"]`
- [ ] `docker-compose.yml`:
  ```yaml
  services:
    postgres:
      image: postgres:16-alpine
      environment:
        POSTGRES_USER: vlsi_dev
        POSTGRES_PASSWORD: ${DB_PASSWORD}
        POSTGRES_DB: ee_vlsi_platform
      volumes:
        - pgdata:/var/lib/postgresql/data
      ports:
        - "5432:5432"

    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"

    api:
      build: .
      command: uvicorn app.main:app --host 0.0.0.0 --port 8000
      ports:
        - "8000:8000"
      env_file: .env
      volumes:
        - ./firebase-sa.json:/app/firebase-sa.json:ro
      depends_on:
        postgres:
          condition: service_healthy
        redis:
          condition: service_started

    worker:
      build: .
      command: python -m app.workers.announcement_worker
      env_file: .env
      volumes:
        - ./firebase-sa.json:/app/firebase-sa.json:ro
      depends_on:
        postgres:
          condition: service_healthy
        redis:
          condition: service_started

  volumes:
    pgdata:
  ```
- [ ] `docker-compose.override.yml` — Dev overrides:
  - Volume mounts for hot reload (`./app:/app/app`)
  - `--reload` flag for uvicorn
- [ ] Add a `healthcheck` to the `postgres` service using `pg_isready`
- [ ] Add migration runner: either as a startup script in the API container or as a one-off service:
  ```yaml
  migrate:
    build: .
    command: alembic upgrade head
    env_file: .env
    depends_on:
      postgres:
        condition: service_healthy
  ```

#### Final Integration Testing Checklist
- [ ] End-to-end announcement flow: CR posts → API returns 202 → Worker processes → WhatsApp webhook fires → Task result written to Redis
- [ ] Resource upload flow: Intent validation → Signed URL → Upload to Storage → Register metadata → Admin approval → Catalogue visibility
- [ ] Auth flow: Register → Pending → Admin approves → Role assigned → Protected routes accessible
- [ ] RBAC matrix: Verify every endpoint against all three roles
- [ ] Pagination: Verify LIMIT/OFFSET pagination on all list endpoints
- [ ] Error handling: Verify all error responses follow a consistent JSON structure:
  ```json
  {"detail": "Human-readable message", "error_code": "UNIQUE_ERROR_CODE"}
  ```
- [ ] Database integrity: Run `SELECT * FROM pg_constraints;` — all FKs, unique constraints, and enums intact

### Testing & Verification
1. `docker-compose up --build` — All four services should start and pass health checks
2. Run `docker-compose run --rm migrate` to apply all Alembic migrations
3. Run the full test matrix from Postman/Swagger against the containerized API (`localhost:8000`)
4. Kill the worker container while tasks are queued → restart → verify tasks are processed (durability test)
5. Kill Redis container → API should return `503 Service Unavailable` on announcement creation, NOT crash
6. Kill PostgreSQL container → API should return `503` on data endpoints (graceful degradation)
7. Check Docker logs for all services — no unhandled exceptions, no leaked secrets
8. If using real WhatsApp webhook: post an announcement and verify the message arrives

### Conceptual Pitfalls

> [!CAUTION]
> **Secrets in Docker images**: Never `COPY .env` or service account JSON into the Docker image. Use environment variables at runtime and mount the SA JSON as a read-only volume.

> [!WARNING]
> **Database migrations in containers**: Alembic migrations should run BEFORE the API starts accepting traffic. Either:
> 1. Run migrations as a separate one-off container (recommended — `docker-compose run --rm migrate`)
> 2. Run `alembic upgrade head` in a startup script inside the API container (simpler but couples concerns)
>
> Never let the API serve requests against an un-migrated database.

- **PostgreSQL data persistence**: The `pgdata` volume ensures your data survives container restarts. Without it, `docker-compose down` destroys your database. Always use named volumes for stateful services.
- **Connection strings in containers**: Inside Docker, services refer to each other by service name (`postgres`, `redis`), not `localhost`. Your `DATABASE_URL` in the container env becomes: `postgresql+asyncpg://vlsi_dev:password@postgres:5432/ee_vlsi_platform`. Different from your local dev URL.
- **Health check depth**: Your API health check should ping PostgreSQL (`SELECT 1`) and Redis (`PING`), not just return `200`. This detects a "running but disconnected" state.

---

## Appendix A — Dependency Manifest

| Package | Purpose | Milestone |
|---|---|---|
| `fastapi` | ASGI web framework | 0 |
| `uvicorn[standard]` | ASGI server | 0 |
| `pydantic-settings` | Env-driven configuration | 0 |
| `python-dotenv` | `.env` file loading | 0 |
| `sqlalchemy[asyncio]` | Async ORM + query builder | 1 |
| `asyncpg` | PostgreSQL async driver | 1 |
| `alembic` | Schema migration tool | 1 |
| `firebase-admin` | Firebase Auth + Storage Admin SDK | 1 |
| `google-cloud-storage` | Signed URL generation for uploads | 6 |
| `redis[hiredis]` | Async Redis client with C parser | 8 |
| `httpx` | Async HTTP client (for webhook calls) | 10 |
| `pytest` | Test framework | All |
| `pytest-asyncio` | Async test support | All |

---

## Appendix B — Architectural Invariants

These rules apply across ALL milestones. Violating any of them will create compounding technical debt.

1. **Routes never touch SQLAlchemy sessions directly.** Route → Service → Repository → Session. No shortcuts.
2. **One session per request.** Created by the `get_db_session` dependency. Never shared across requests. Never created inside a repository.
3. **All relationship loading is explicit.** Use `selectinload()` or `joinedload()` in every query that accesses related objects. Never rely on lazy loading — it doesn't work with `AsyncSession`.
4. **All response models are Pydantic schemas.** No raw dicts returned from routes. No SQLAlchemy models leaked to the API layer.
5. **All errors return structured JSON.** Use FastAPI exception handlers to standardize error responses. Catch `IntegrityError` at the service layer — never let database exceptions reach the client.
6. **All protected routes use dependency injection.** No manual `if role != "ADMIN"` checks inside route bodies. Use `Depends(require_admin)`.
7. **All timestamps are UTC ISO 8601.** Store as `TIMESTAMP WITH TIME ZONE` in PostgreSQL. Frontend converts to display timezone.
8. **All IDs are UUIDs in the API.** Consistent, unforgeable, and database-agnostic.
9. **Migrations are immutable once applied.** Never edit a migration file after running it. Create a new migration to make changes.
10. **Logging, not print statements.** Use Python's `logging` module from day one. Structured JSON logs are ideal for Docker log aggregation.

---

## Appendix C — Build Order Dependency Graph

```mermaid
graph TD
    M0["M0: Scaffolding"] --> M1["M1: PostgreSQL + SQLAlchemy"]
    M1 --> M2["M2: Auth Middleware"]
    M2 --> M3["M3: RBAC Layer"]
    M3 --> M4["M4: Users & Directory"]
    M3 --> M5["M5: Announcements"]
    M3 --> M7["M7: Chronicles"]
    M4 --> M9["M9: Hall of Fame & Forge"]
    M5 --> M8["M8: Redis & Workers"]
    M3 --> M6["M6: Vault & Storage"]
    M8 --> M10["M10: WhatsApp & Docker"]
    M9 --> M10
    M6 --> M10
    M7 --> M10

    style M0 fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style M1 fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style M2 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style M3 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style M4 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style M5 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style M6 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style M7 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style M8 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style M9 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    style M10 fill:#fce4ec,stroke:#c62828,stroke-width:2px
```

> [!NOTE]
> **Parallelizable milestones**: After M3 (RBAC), milestones M4, M5, M6, and M7 are independent of each other. You can tackle them in any order. M8 depends on M5 (announcements must exist before you queue them). M10 depends on everything.

---

## Appendix D — Testing Without a Frontend: Your Workflow

Since you're building backend-first, here's your daily testing workflow:

1. **Swagger UI** (`/docs`): Primary tool for manual endpoint testing. Use the 🔒 button to set your Bearer token globally.
2. **Firebase Auth REST API**: To generate test tokens without a frontend:
   ```
   POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=YOUR_API_KEY
   ```
3. **Postman Collections**: Build a collection per milestone. Use Postman environments to store tokens and IDs. Export and commit the collection JSON (sanitize secrets).
4. **psql CLI**: Your best friend for verifying data integrity:
   ```bash
   # Connect to your local database
   psql -U vlsi_dev -d ee_vlsi_platform

   # Useful commands
   \dt                              -- List all tables
   \d users                         -- Describe table schema
   SELECT * FROM users;             -- Check data
   SELECT * FROM pg_indexes;        -- Check indexes
   EXPLAIN ANALYZE SELECT ...;      -- Check query performance
   ```
5. **Redis CLI**: Monitor your queues in real-time:
   ```bash
   redis-cli MONITOR                       # Watch all commands
   redis-cli LLEN queue:announcements      # Check queue depth
   redis-cli HGETALL task_results:{id}     # Check task result
   ```
6. **One-off scripts**: For operations like setting Firebase custom claims or seeding test data, write small scripts in the `scripts/` directory.
7. **Alembic commands** you'll use constantly:
   ```bash
   alembic revision --autogenerate -m "description"   # Generate migration
   alembic upgrade head                                # Apply all pending
   alembic downgrade -1                                # Rollback one
   alembic history                                     # View migration history
   alembic current                                     # Check current version
   ```
