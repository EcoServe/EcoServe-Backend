# app/extensions.py
import os
import redis
from rq import Queue
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per minute"])

# RQ (Redis Queue) — provide a Queue object called `rq`
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
redis_conn = redis.from_url(REDIS_URL)
rq = Queue("default", connection=redis_conn)
