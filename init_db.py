"""
One-time database initializer.

Reads the connection details from your .env (DATABASE_URL if set, otherwise the
DB_* fields) and loads the PostgreSQL schema and demo data into that database.

Usage:
    python init_db.py           # load schema + demo data
    python init_db.py --schema  # load schema only (no demo data)
"""
import sys
from src.database.database import connect_db

SCHEMA_FILE = "00 its sql SQL/01 schema_postgres.sql"
SEED_FILE = "00 its sql SQL/02 run_queries_postgres.sql"


def run_sql_file(path):
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    db = connect_db()
    cur = db.cursor()
    cur.execute(sql)
    db.commit()
    db.close()
    print(f"  OK -> {path}")


def main():
    print("Connecting and loading schema...")
    run_sql_file(SCHEMA_FILE)
    if "--schema" not in sys.argv:
        print("Loading demo data (login: test / test)...")
        run_sql_file(SEED_FILE)
    print("Done. Database is ready.")


if __name__ == "__main__":
    main()
