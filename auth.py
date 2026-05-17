from flask_login import LoginManager

from models import User
from db import db


login_manager = LoginManager()
login_manager.login_view = "auth.login"


def init_auth(app):
    login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


def current_user_id():
    try:
        from flask_login import current_user
        if current_user.is_authenticated:
            return current_user.user_id
        return None
    except Exception:
        return None


def is_admin():
    try:
        from flask_login import current_user
        return current_user.is_authenticated and bool(getattr(current_user, "is_admin", False))
    except Exception:
        return False
