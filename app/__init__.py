# app/__init__.py
import os
from flask import Flask
from flask_cors import CORS
from .extensions import db, migrate, login_manager, limiter

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    CORS(app)


    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,           # ← important
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,                    # set True in prod behind HTTPS
        WTF_CSRF_TIME_LIMIT=None,
        RATELIMIT_STORAGE_URI=os.getenv("REDIS_URL", "memory://"),  # ← rate-limit storage
    )

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"            # change to your real login endpoint
    limiter.init_app(app)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    # import after app is created to avoid circular imports
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
