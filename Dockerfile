FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

# نصب Nginx و envsubst
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    gettext-base \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد پروژه
COPY . .

# آماده‌سازی کانفیگ Nginx
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

RUN mkdir -p /data

EXPOSE 8080

# اجرای همزمان Nginx و پنل
CMD ["sh", "-c", "envsubst '$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;' & python start.py"]
