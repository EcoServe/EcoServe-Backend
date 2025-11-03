# app/extensions.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Database & Core Extensions ---
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# --- Rate Limiter (safe for Render free tier) ---
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),  # use memory instead of Redis
    default_limits=os.getenv("DEFAULT_LIMITS", "60 per minute").split(";"),
    enabled=os.getenv("RATELIMIT_ENABLED", "1") == "1",           # can disable via env
)
