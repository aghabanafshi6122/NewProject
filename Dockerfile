FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

WORKDIR /app

# نصب Nginx، envsubst و ابزارهای آزادسازی پورت (fuser از psmisc، lsof)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    gettext-base \
    psmisc \
    lsof \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد پروژه (شامل static/)
COPY . .

# کانفیگ Nginx
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# پوشه داده
RUN mkdir -p /data

EXPOSE 8000

# اجرای Nginx و پنل با هم
CMD ["sh", "-c", "envsubst '$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;' & python start.py"]
