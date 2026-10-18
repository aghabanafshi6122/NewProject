FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

# نصب Nginx و ابزار envsubst برای جایگزینی متغیر $PORT
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    gettext-base \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نصب وابستگی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد پروژه
COPY . .

# کپی و آماده‌سازی کانفیگ Nginx
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# پوشه داده
RUN mkdir -p /data

# اسکریپت شروع: ابتدا Nginx را با envsubst راه‌اندازی می‌کنیم، سپس پنل پایتونی
# نکته: پنل پایتونی باید روی پورت 8000 اجرا شود (نه $PORT)
CMD ["sh", "-c", "envsubst '$$PORT' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;' & python main.py"]
