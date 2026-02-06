"""One-off migration script to add first_dashboard_visit_at column to users table.

Run this once against your existing database:

    python -m app.migrate_add_first_dashboard_visit_at

This is safe to run multiple times; it will no-op if the column already exists.
"""

from sqlalchemy import inspect, text

from app.database import engine


def column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    for col in inspector.get_columns(table_name):
        if col.get("name") == column_name:
            return True
    return False


def main() -> None:
    table = "users"
    column = "first_dashboard_visit_at"

    if column_exists(table, column):
        print(f"Column {column} already exists on {table}, nothing to do.")
        return

    with engine.begin() as conn:
        # SQLite and Postgres both support ADD COLUMN without touching existing rows
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} TIMESTAMP NULL"))
        print(f"Added column {column} to {table}.")


if __name__ == "__main__":
    main()

