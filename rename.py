# rename.py — یک بار اجرا کن: python rename.py
# بعد از اجرا این فایل را حذف کن یا در .dockerignore بگذار.
import os
import re
import json
import secrets
import string

FILES_TO_RENAME = ["pages", "relay_vless", "xhttp_siz10", "telegram_bot", "speed_limit"]

def rand_name(length=8):
    return "x" + "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))

rename_map = {}
for old in FILES_TO_RENAME:
    old_file = f"{old}.py"
    if not os.path.exists(old_file):
        print(f"⚠️ {old_file} پیدا نشد، رد شد")
        continue
    new = rand_name()
    while os.path.exists(f"{new}.py"):
        new = rand_name()
    os.rename(old_file, f"{new}.py")
    rename_map[old] = new
    print(f"✅ {old_file} → {new}.py")

# اصلاح importها در همه فایل‌های .py
for fname in os.listdir("."):
    if not fname.endswith(".py") or fname == "rename.py":
        continue
    with open(fname, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in rename_map.items():
        content = re.sub(rf"\bfrom\s+{old}\b", f"from {new}", content)
        content = re.sub(rf"\bimport\s+{old}\b", f"import {new}", content)
    if content != original:
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"🔧 importها در {fname} اصلاح شد")

with open("rename_map.json", "w", encoding="utf-8") as f:
    json.dump(rename_map, f, ensure_ascii=False, indent=2)

print("\n📋 نقشه در rename_map.json ذخیره شد")
