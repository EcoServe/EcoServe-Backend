# app/__init__.py
import os
from flask import Flask
from .extensions import db, migrate, login_manager, limiter

# ✅ add these imports
from flask_cors import CORS
from sqlalchemy import text

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # --- normalize DATABASE_URL + force SSL ---
    raw_db_url = os.getenv("DATABASE_URL", "")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
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

    # ✅ enable CORS for your Vercel site (replace with your real URL)
    CORS(
        app,
        resources={r"/*": {"origins": [
            "https://eco-serve-frontend.vercel.app",
            "http://localhost:3000"  # optional for local testing
        ]}}
    )

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    limiter.init_app(app)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    # ✅ use sqlalchemy.text for /dbcheck
    @app.get("/dbcheck")
    def dbcheck():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500

    # blueprints
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

        # ---------------------------------------------------------------------
    # Frontend compatibility aliases (map older/different paths to real ones)
    # Add these *after* blueprints are registered.

    def _alias(url_rule: str, target_endpoint: str, methods: list[str]):
        """
        Reuse an existing view function (by endpoint name) under another URL.
        Example target_endpoint values you can see in /__routes output, e.g.
        'deposits.create_deposit', 'rewards.list_rewards', etc.
        """
        app.add_url_rule(
            url_rule,
            endpoint=f"alias:{url_rule}",
            view_func=app.view_functions[target_endpoint],
            methods=methods,
        )

    # If frontend posts to /api/deposit, send it to real POST /api/deposits
    _alias("/api/deposit", "deposits.create_deposit", ["POST"])

    # If frontend expects /api/reward/list or /api/rewards/list → GET /api/rewards
    _alias("/api/reward/list", "rewards.list_rewards", ["GET"])
    _alias("/api/rewards/list", "rewards.list_rewards", ["GET"])

    # If frontend posts to /api/reward/redeem → real POST /api/redeem
    _alias("/api/reward/redeem", "rewards.redeem", ["POST"])

    # If frontend uses /api/pickup/list → real GET /api/pickups
    _alias("/api/pickup/list", "pickups.list_pickups", ["GET"])

    # If frontend uses /api/pickup/update/<bid> (PUT) → real PUT /api/pickups/<bid>
    _alias("/api/pickup/update/<int:bid>", "pickups.update_pickup", ["PUT"])

    # If frontend uses /api/login → real POST /api/auth/otp
    _alias("/api/login", "auth.otp", ["POST"])

    # If frontend uses /api/verify → real POST /api/auth/verify
    _alias("/api/verify", "auth.verify", ["POST"])
    # ---------------------------------------------------------------------


    @app.route("/")
    def index():
        return "🚀 Ecoserve backend is running successfully!"
    
    # ---------------------------------------------------------------------
    # DEBUG: list all routes
    @app.get("/__routes")
    def __routes():
        out = []
        for r in app.url_map.iter_rules():
            methods = ",".join(sorted(m for m in r.methods if m not in ("HEAD", "OPTIONS")))
            out.append({"rule": str(r), "endpoint": r.endpoint, "methods": methods})
        return {"routes": out}

    # DEBUG: quick DB test
    @app.get("/__dbtest")
    def __dbtest():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500
    # ---------------------------------------------------------------------
    
    return app
