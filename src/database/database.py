
import psycopg2
import psycopg2.extras
from src.logic.config import Config
from datetime import timedelta


# ---------------------------------------------------------------------------
# PostgreSQL compatibility layer.
#
# The rest of the application was written against the mysql.connector API
# (e.g. `db.cursor(dictionary=True)` and `cursor.lastrowid`). To migrate to
# PostgreSQL without touching any application/route/algorithm code, we wrap
# the psycopg2 connection and cursor so they expose that same interface.
# psycopg2 already uses the same `%s` parameter placeholder as mysql.connector,
# so the SQL strings in the app work unchanged.
# ---------------------------------------------------------------------------


class _CursorWrapper:
    """Emulates the parts of the mysql.connector cursor API the app relies on."""

    def __init__(self, cursor):
        self._cursor = cursor
        self._lastrowid = None

    def execute(self, operation, params=None):
        query = operation
        is_insert = (
            operation.lstrip()[:6].upper() == "INSERT"
            and "RETURNING" not in operation.upper()
        )
        # mysql.connector exposes the new PK via `cursor.lastrowid`; PostgreSQL
        # needs an explicit RETURNING clause. Append one to plain INSERTs so we
        # can capture the generated primary key transparently.
        if is_insert:
            query = operation.rstrip().rstrip(";") + " RETURNING *"

        self._cursor.execute(query, params)

        if is_insert:
            try:
                row = self._cursor.fetchone()
                if row is None:
                    self._lastrowid = None
                elif isinstance(row, dict):
                    self._lastrowid = next(iter(row.values()))
                else:
                    self._lastrowid = row[0]
            except psycopg2.ProgrammingError:
                self._lastrowid = None

    @property
    def lastrowid(self):
        return self._lastrowid

    def __getattr__(self, name):
        # Delegate everything else (fetchone, fetchall, close, description, ...)
        return getattr(self._cursor, name)


class _ConnectionWrapper:
    """Emulates the mysql.connector connection API used by the app."""

    def __init__(self, conn):
        self._conn = conn

    def cursor(self, dictionary=False, **kwargs):
        if dictionary:
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            cur = self._conn.cursor()
        return _CursorWrapper(cur)

    def __getattr__(self, name):
        # Delegate commit, rollback, close, etc.
        return getattr(self._conn, name)


def connect_db():
    if Config.DATABASE_URL:
        # A full connection URL (e.g. from Neon/Supabase) is used as-is.
        conn = psycopg2.connect(Config.DATABASE_URL)
    else:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dbname=Config.DB_NAME,
            port=Config.DB_PORT,
            sslmode=Config.DB_SSLMODE,
        )
    return _ConnectionWrapper(conn)

def fetch_data(class_name, semester, school_id):
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("SELECT class_id FROM class WHERE class_name = %s AND school_id = %s", (class_name, school_id))
    class_id = cursor.fetchone()

    if class_id is None:
        return [], []

    class_id = class_id[0]
    cursor.execute("SELECT subject_name FROM subject WHERE class_id = %s AND semester = %s AND school_id = %s", (class_id, semester, school_id))
    subjects = [row[0] for row in cursor.fetchall()]

    # Timeslots are now generic or per allocation?
    # For now, sticking to logic where we just need a list?
    # Actually, timeslots come from school config now usually.
    # But let's keep this query valid just in case.
    cursor.execute("SELECT timeslot FROM timeslot")
    timeslots = [row[0] for row in cursor.fetchall()]

    db.close()
    return subjects, timeslots

def get_timetable_by_class(class_name, semester, school_id):
    db = connect_db()
    cursor = db.cursor()

    # Get class_id
    cursor.execute("SELECT class_id FROM class WHERE class_name = %s AND school_id = %s", (class_name, school_id))
    result = cursor.fetchone()
    if not result:
        db.close()
        return {}, []

    class_id = result[0]

    # Fetch timetable with day and timeslot
    query = """
    SELECT s.subject_name, t.day, ts.timeslot
    FROM timetable t
    JOIN subject s ON t.subject_id = s.subject_id
    JOIN timeslot ts ON t.time_id = ts.time_id
    WHERE t.class_id = %s AND s.semester = %s AND t.school_id = %s
    """
    cursor.execute(query, (class_id, semester, school_id))
    results = cursor.fetchall()

    # Fetch all timeslots for structure
    cursor.execute("SELECT timeslot FROM timeslot")
    all_timeslots = [str(row[0]) for row in cursor.fetchall()]

    db.close()

    timetable = {}
    for subject, day, timeslot in results:
        if isinstance(timeslot, timedelta):
            # Format timedelta to HH:MM:SS with leading zero for hour
            total_seconds = int(timeslot.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            timeslot = f"{hours:02}:{minutes:02}:{seconds:02}"
        timetable[f"{day}_{timeslot}"] = subject

    return timetable, sorted(all_timeslots)
