import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_dev_key')
    # Managed providers (Neon, Supabase, ...) and most deploy platforms give a
    # single connection URL. If set, it takes precedence over the fields below.
    DATABASE_URL = os.environ.get('DATABASE_URL')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
    DB_NAME = os.environ.get('DB_NAME', 'timetable_db')
    DB_PORT = int(os.environ.get('DB_PORT', '5432'))
    # 'prefer' uses SSL if the server supports it and silently falls back to a
    # plain connection otherwise, so a default local PostgreSQL works as-is.
    DB_SSLMODE = os.environ.get('DB_SSLMODE', 'prefer')
