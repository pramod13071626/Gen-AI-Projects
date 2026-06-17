import os

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:  # pragma: no cover - fallback for missing optional dependency
    class SQLAlchemy:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def init_app(self, app):
            raise ImportError("flask_sqlalchemy is required to initialize the database")

db = SQLAlchemy()


def init_db(app):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/medilife"

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", db_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)
    return db
