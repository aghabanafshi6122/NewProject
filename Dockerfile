FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

# وابستگی‌های سیستمی (در صورت نیاز به کامپایل)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# اول فقط requirements را کپی کن (کش لایه)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# بعد بقیه کد
COPY . .

# پوشه داده (Railway Volume اینجا مانت می‌شود)
RUN mkdir -p /data

EXPOSE 8000

CMD ["python", "main.py"]
