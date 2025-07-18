# Design and Principles

- Simple python template I am experimenting with around a set of overlapping concepts with a Fastapi implementation, primarily:
  - Vertical Slice
  - With elements of:
    - Domain Driven Design (DDD)
    - Clean Architecture
    - Ports & Adapters
    - CQRS

## Pair Programming Rules

- do not make git commits
- pair program with the human developer with <https://github.com/remotemobprogramming/mob> framework
- human developer will the only one who executes `mob done`
- agent will execute `mob start` when coding starts
- agent will execute `mob next` when coding is complete and ready for review

## Core System Components

- The main application logic is in app.
- Feature flags and configuration settings are in config.py.

## Code styles

- Use PEP 8 and pythonic code
- Use type hints
- Functions: Use `snake_case`
- Variables: Use `snake_case`
- Constants: Use `UPPER_CASE`
- Classes: Use `CamelCase`
- Use `uv` for dependency management
- Use `pyenv` for python version management
- Use `loguru` for logging
- Use `pydantic` for data validation
- Use `sqlmodel` for database interactions
- Use `pydantic-settings` for configuration
- Use `python-dotenv` for environment variables
- Use `pytest` for testing
- Use `pytest-cov` for coverage

## Data & Storage

- Support for Sqlite and Postgres via sqlmodel.
- Use `atlas` for database migrations
- Use `migrations` directory for migration files
- Use Bytebase and Supabase style guides
- Identifier Style: snake_case, lowercase, descriptive
- Table Names: snake_case, plural, no prefixes, descriptive
- Column Names: snake_case, singular, descriptive, avoid generic, with `_id`
- Data Types: Prefer specific types, ENUM for small sets, avoid CHAR(n)
- Query Formatting: Lowercase keywords, whitespace, clear indentation
- Functions: Lowercase, snake_case
- Constraints: Explicit, descriptive names

## Testing & Debugging

- Unit, component and integration tests in app/tests
- Create unit and component tests first before writing the actual code
- Follow code implementation with integration tests

## Workflow and developer interaction

- TBD

## Bash commands

- Running api server:

```bash
uv run fastapi dev main.py
```

- Running tests:

```bash
uv run pytest
```

- Running database and migrations:

```bash
docker compose up
docker compose down -v
```

- Various migration commands depending on database type:

```bash
atlas schema inspect -u "sqlite://file?cache=shared&mode=memory" --format "{{ sql . }}"
atlas schema inspect -u "sqlite://issues.db" --format "{{ sql . }}" > migrate.sql
atlas schema inspect -u "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --schema "issue_analysis" --format "{{ sql . }}"

atlas schema apply --url "sqlite://issues.db" --to "file://migrate.sql" --dev-url "sqlite://file?mode=memory" --dry-run
atlas schema apply --url "sqlite://issues.db" --to "file://migrate.sql" --dev-url "sqlite://file?mode=memory"

atlas schema apply --url "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --to "file://./migrations/migrate.sql" --dev-url "docker://postgres/17" --dry-run
atlas schema apply --url "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --to "file://./migrations/migrate.sql" --dev-url "docker://postgres/17"
```
