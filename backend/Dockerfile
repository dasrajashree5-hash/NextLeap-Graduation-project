FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt psycopg[binary]>=3.2.0

COPY . .

EXPOSE 8000

# Railway sets PORT at runtime; exec-form CMD does not expand $PORT, so use sh -c.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
