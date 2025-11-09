# app/__init__.py
import os
import re
from flask import Flask
from .extensions import db, migrate, login_manager, limiter
from flask_cors import CORS
from sqlalchemy import text


def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # ---------------- Database URL normalize (+ SSL for Render Postgres) ----------------
    raw_db_url = os.getenv("DATABASE_URL", "")
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if raw_db_url and "sslmode=" not in raw_db_url:
        sep = "&" if "?" in raw_db_url else "?"
        raw_db_url = f"{raw_db_url}{sep}sslmode=require"

    # ---------------- App Config (cookies set correctly for cross-site in prod) --------
    is_prod = os.getenv("FLASK_ENV") == "production"
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=raw_db_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_SAMESITE="None" if is_prod else "Lax",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True if is_prod else False,
        WTF_CSRF_TIME_LIMIT=None,
        RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
    )

    # ---------------- CORS (allow your Vercel app + localhost + preview branches) ------
    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "https://eco-serve-frontend-imxr.vercel.app"  # your deployed frontend
    )
    allowed_origins = [
        FRONTEND_ORIGIN,                              # production vercel app
        "http://localhost:3000",                      # local dev
        re.compile(r"^https://.*\.vercel\.app$"),     # preview branches
    ]
    CORS(
        app,
        resources={r"/*": {"origins": allowed_origins}},  # cover all routes incl. ones without /api prefix
        supports_credentials=True,
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        expose_headers=["Content-Type"],
    )

    # ---------------- Init extensions ---------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    limiter.init_app(app)

    # ---------------- Health + DB check -------------------------------------------------
    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/dbcheck")
    def dbcheck():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500

    # ---------------- Blueprints --------------------------------------------------------
    from .auth.routes import bp as auth_bp
    from .deposits.routes import bp as deposits_bp
    from .admin.routes import bp as admin_bp
    from .rewards.routes import bp as rewards_bp
    from .pickups.routes import bp as pickups_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(deposits_bp)                   # NOTE: no prefix; routes may live at /deposits
    app.register_blueprint(admin_bp, url_prefix="/api")
    app.register_blueprint(rewards_bp, url_prefix="/api")
    app.register_blueprint(pickups_bp, url_prefix="/api")

    # ---------------- Frontend compatibility aliases -----------------------------------
    def _alias(url_rule: str, target_endpoint: str, methods: list[str]):
        app.add_url_rule(
            url_rule,
            endpoint=f"alias:{url_rule}",
            view_func=app.view_functions[target_endpoint],
            methods=methods,
        )

    _alias("/api/deposit", "deposits.create_deposit", ["POST"])
    _alias("/api/reward/list", "rewards.list_rewards", ["GET"])
    _alias("/api/rewards/list", "rewards.list_rewards", ["GET"])
    _alias("/api/reward/redeem", "rewards.redeem", ["POST"])
    _alias("/api/pickup/list", "pickups.list_pickups", ["GET"])
    _alias("/api/pickup/update/<int:bid>", "pickups.update_pickup", ["PUT"])
    _alias("/api/login", "auth.otp", ["POST"])
    _alias("/api/verify", "auth.verify", ["POST"])

    # ---------------- Root + debug helpers ---------------------------------------------
    @app.route("/")
    def index():
        return "🚀 Ecoserve backend is running successfully!"

    @app.get("/__routes")
    def __routes():
        out = []
        for r in app.url_map.iter_rules():
            methods = ",".join(sorted(m for m in r.methods if m not in ("HEAD", "OPTIONS")))
            out.append({"rule": str(r), "endpoint": r.endpoint, "methods": methods})
        return {"routes": out}

    @app.get("/__dbtest")
    def __dbtest():
        try:
            db.session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as e:
            return {"db": "error", "detail": str(e)}, 500

    return app
