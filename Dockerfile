FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use Gunicorn for production serving
CMD ["gunicorn", "run:app", "-b", "0.0.0.0:5000", "--workers=2", "--threads=2", "--timeout=60", "--max-requests=200", "--max-requests-jitter=50", "--log-level", "info"]

