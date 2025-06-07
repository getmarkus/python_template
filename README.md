# my personal python template playground

Simple python template I am experimenting with around a set of overlapping concepts with a Fastapi implementation:

- DDD
- Clean architecture
- Ports/Adapters
- Vertical slice

```bash
uv run fastapi dev main.py
uv run pytest

docker compose up
docker compose down -v

atlas schema inspect -u "sqlite://file?cache=shared&mode=memory" --format "{{ sql . }}"
atlas schema inspect -u "sqlite://issues.db" --format "{{ sql . }}" > migrate.sql
atlas schema inspect -u "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --schema "issue_analysis" --format "{{ sql . }}"

atlas schema apply --url "sqlite://issues.db" --to "file://migrate.sql" --dev-url "sqlite://file?mode=memory" --dry-run
atlas schema apply --url "sqlite://issues.db" --to "file://migrate.sql" --dev-url "sqlite://file?mode=memory"

atlas schema apply --url "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --to "file://./migrations/migrate.sql" --dev-url "docker://postgres/17" --dry-run
atlas schema apply --url "postgres://app_user:change_this_password@localhost:5432/app_database?sslmode=disable" --to "file://./migrations/migrate.sql" --dev-url "docker://postgres/17"
```
