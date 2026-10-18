# rename.py — یک بار اجرا کن: python rename.py
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

# اصلاح importها
for fname in os.listdir("."):
    if not fname.endswith(".py") or fname in ("rename.py", "open_page.py"):
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

# ── تغییر main.py: پورت 2026 + ثبت /open ────────────────────────────────────
if os.path.exists("main.py"):
    with open("main.py", "r", encoding="utf-8") as f:
        m = f.read()

    # پورت پیش‌فرض 8000 → 2026
    m2 = m.replace(
        '"port": int(os.environ.get("PORT", 8000)),',
        '"port": int(os.environ.get("PORT", 2026)),'
    )
    if m2 != m:
        print("🔧 پورت پیش‌فرض main.py به 2026 تغییر کرد")
        m = m2

    # اضافه کردن ثبت open_page قبل از خط main
    marker = 'if __name__ == "__main__":'
    if marker in m and "register_open_page" not in m:
        inject = (
            "# ── /open (auto-injected by rename.py) ─────────────────────────────\n"
            "from open_page import register as register_open_page\n"
            "register_open_page(app, require_auth)\n\n"
        )
        m = m.replace(marker, inject + marker, 1)
        print("🔧 ثبت /open به main.py اضافه شد")

    with open("main.py", "w", encoding="utf-8") as f:
        f.write(m)

with open("rename_map.json", "w", encoding="utf-8") as f:
    json.dump(rename_map, f, ensure_ascii=False, indent=2)

print("\n📋 نقشه در rename_map.json ذخیره شد")
