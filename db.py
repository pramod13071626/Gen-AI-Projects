import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = "postgresql+psycopg2://postgres:postgres@localhost:5432/medilife"

    app.config.setdefault("SQLALCHEMY_DATABASE_URI", db_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)
    return db
