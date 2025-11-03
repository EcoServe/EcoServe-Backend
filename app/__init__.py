# app/__init__.py
import os
from flask import Flask
from .extensions import db, migrate, login_manager, limiter

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # --- FIX: normalize DATABASE_URL for SQLAlchemy + psycopg2 and add SSL ---
    raw_db_url = os.getenv("DATABASE_URL", "")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    # add sslmode=require if not present
    if raw_db_url and "sslmode=" not in raw_db_url:
        sep = "&" if "?" in raw_db_url else "?"
        raw_db_url = f"{raw_db_url}{sep}sslmode=require"

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=raw_db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,
        WTF_CSRF_TIME_LIMIT=None,
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )
    # -------------------------------------------------------------------------

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    limiter.init_app(app)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}
    
    @app.get("/dbcheck")
    def dbcheck():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"db": "ok"}
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500


    from .auth.routes import bp as auth_bp
    from .deposits.routes import bp as deposits_bp
    from .admin.routes import bp as admin_bp
    from .rewards.routes import bp as rewards_bp
    from .pickups.routes import bp as pickups_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(deposits_bp)
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(rewards_bp, url_prefix="/api")
    app.register_blueprint(pickups_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return "🚀 Ecoserve backend is running successfully!"

    return app
