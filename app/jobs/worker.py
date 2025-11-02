from rq import Connection, Worker
from app.extensions import redis_conn

if __name__ == "__main__":
    with Connection(redis_conn):
        Worker(["ecoserve"]).work()
