FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/start.sh

EXPOSE 8000

# Railway injects PORT; start.sh expands it in a shell (see scripts/start.sh).
CMD ["sh", "scripts/start.sh"]
