# Generative Timetable using Genetic Algorithm

An automated system to generate optimized college/university timetables using Artificial Intelligence (Genetic Algorithm). This project ensures no scheduling conflicts, respects subject priorities, and optimizes resource allocation.

## 🚀 Getting Started

Follow these steps to set up the project on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/Aanand2204/Generative-Timetable-using-Genetic-Algorithm.git
cd Generative-Timetable-using-Genetic-Algorithm
```

### 2. Prerequisites
- Python 3.8+
- PostgreSQL (local server)

### 3. Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables (.env)
The application requires several environment variables for database connectivity and security.
- Create a file named `.env` in the root directory.
- Use `.env.example` as a template.
- **Note:** Ensure you configure your database credentials correctly in this file.

Example `.env` content (local PostgreSQL):
```env
SECRET_KEY=your_random_secret_key
DB_HOST=localhost
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=timetable_db
DB_PORT=5432
DB_SSLMODE=prefer
```

### 6. Database Setup
The database lives in a local **PostgreSQL** server.

1. Create a database named `timetable_db`:
   ```bash
   createdb -U postgres timetable_db
   ```
2. Import the schema, then optionally the demo data:
   ```bash
   psql -U postgres -d timetable_db -f "00 its sql SQL/01 schema_postgres.sql"
   psql -U postgres -d timetable_db -f "00 its sql SQL/02 run_queries_postgres.sql"
   ```
   The demo data lets you log in with username `test` / password `test`.

### 7. Run the Application
```bash
python app.py
```
After running, the server should be available at `http://127.0.0.1:5000`.

## ☁️ Deployment (so others can use it)

A database on your own machine (`localhost`) is only reachable from your machine. To put the app online for other people, host the database on a **free managed PostgreSQL** provider such as [Neon](https://neon.tech/) or [Supabase](https://supabase.com/) — no application code changes are needed, only environment variables.

1. Create a free project on Neon or Supabase and copy its **connection URL**
   (looks like `postgresql://user:password@host/dbname?sslmode=require`).
2. Load the schema into that database (run once, from your machine):
   ```bash
   psql "postgresql://user:password@host/dbname?sslmode=require" -f "00 its sql SQL/01 schema_postgres.sql"
   # optional demo data:
   psql "postgresql://user:password@host/dbname?sslmode=require" -f "00 its sql SQL/02 run_queries_postgres.sql"
   ```
3. On your host (and in `.env` for local testing against it), set a single variable:
   ```env
   DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
   ```
   When `DATABASE_URL` is set it overrides the individual `DB_*` fields, so you can keep those pointed at local PostgreSQL for development.

## 🛠️ Tech Stack
- **Backend:** Flask (Python)
- **Algorithm:** Genetic Algorithm
- **Database:** PostgreSQL
- **Frontend:** HTML/CSS/JavaScript (located in `templates/` and `static/`)

