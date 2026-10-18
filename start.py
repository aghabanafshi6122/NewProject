# start.py — نسخه نهایی
# - تلاش می‌کند پورت 8080 را آزاد کند
# - اگر نشد، روی 8081 اجرا می‌شود
# - مسیر /open را اضافه می‌کند
import os
import json
import time
import signal
import subprocess
import uvicorn
from fastapi import Depends
from fastapi.responses import HTMLResponse

from main import app, require_auth


# ── /open : نقشه تغییر نام فایل‌ها ────────────────────────────────────────────
@app.get("/open", response_class=HTMLResponse)
async def open_page(_=Depends(require_auth)):
    try:
        with open("rename_map.json", "r", encoding="utf-8") as f:
            rename_map = json.load(f)
    except FileNotFoundError:
        rename_map = {}

    rows = "".join(
        f"<tr><td><code>{old}.py</code></td><td style='color:#A78BFA'>→</td>"
        f"<td><code>{new}.py</code></td></tr>"
        for old, new in rename_map.items()
    ) or "<tr><td colspan='3' style='color:#6D4A9E'>هیچ فایلی تغییر نام نداده است</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><title>نقشه تغییر نام · Purple-Panel</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;600;800&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Vazirmatn',sans-serif;background:#0f081a;color:#F0E8FF;min-height:100vh;padding:40px 20px;display:flex;align-items:flex-start;justify-content:center}}
.card{{background:#160c28;border:1px solid rgba(139,92,246,.25);border-radius:20px;padding:32px 36px;max-width:560px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,.5)}}
h1{{color:#A78BFA;font-size:20px;margin-bottom:8px;display:flex;align-items:center;gap:10px}}
p{{color:#9C8ABF;font-size:13px;margin-bottom:22px;line-height:1.8}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:11px 14px;text-align:right;font-size:13px}}
th{{color:#6D4A9E;font-size:11px;text-transform:uppercase;letter-spacing:.06em;border-bottom:1px solid rgba(139,92,246,.2)}}
td{{border-bottom:1px solid rgba(139,92,246,.07)}}
tr:last-child td{{border-bottom:none}}
code{{background:#1a0e30;padding:4px 10px;border-radius:6px;color:#C4B5FD;font-family:ui-monospace,monospace;font-size:12px}}
.back{{display:inline-block;margin-top:22px;color:#A78BFA;text-decoration:none;font-size:13px;font-weight:600}}
.back:hover{{color:#C4B5FD}}
</style></head>
<body>
<div class="card">
<h1>🗺️ نقشه تغییر نام فایل‌ها</h1>
<p>این فایل‌ها با اسم رندوم جایگزین شده‌اند تا ساختار پروژه کمی پنهان‌تر باشد.</p>
<table>
<tr><th>اسم اصلی</th><th></th><th>اسم جدید</th></tr>
{rows}
</table>
<a class="back" href="/dashboard">⬅ بازگشت به داشبورد</a>
</div>
</body></html>"""
    return HTMLResponse(html)


# ── ابزار آزادسازی پورت ──────────────────────────────────────────────────────
def free_port(port: int, wait: float = 1.5) -> bool:
    """تلاش می‌کند هر فرآیندی که روی port گوش می‌دهد را kill کند.
    اگر موفق شود یا پورت از قبل آزاد بود True برمی‌گرداند."""
    killed = False

    # روش ۱: fuser
    try:
        r = subprocess.run(
            ["fuser", f"{port}/tcp"],
            capture_output=True, text=True, timeout=5
        )
        if r.stdout.strip():
            for pid in r.stdout.strip().split():
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    killed = True
                except (ProcessLookupError, ValueError, PermissionError):
                    pass
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    # روش ۲: lsof (اگر fuser نبود)
    if not killed:
        try:
            r = subprocess.run(
                ["lsof", "-t", f"-i:{port}"],
                capture_output=True, text=True, timeout=5
            )
            if r.stdout.strip():
                for pid in r.stdout.strip().split():
                    try:
                        os.kill(int(pid), signal.SIGKILL)
                        killed = True
                    except (ProcessLookupError, ValueError, PermissionError):
                        pass
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

    if killed:
        time.sleep(wait)
        return True
    return False


def is_port_free(port: int) -> bool:
    """بررسی می‌کند آیا پورت آزاد است یا نه (بدون تلاش برای kill)."""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.bind(("127.0.0.1", port))
        s.close()
        return True
    except OSError:
        s.close()
        return False


# ── اجرا ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # سعی می‌کنیم 8080 را آزاد کنیم
    if not is_port_free(8080):
        print("[start.py] پورت 8080 اشغال است، تلاش برای آزادسازی...")
        free_port(8080)

    if is_port_free(8080):
        chosen_port = 8080
    else:
        print("[start.py] پورت 8080 هنوز اشغال است، استفاده از 8081")
        free_port(8081)  # اگر 8081 هم اشغال بود، آزادش کن
        chosen_port = 8081

    print(f"[start.py] اجرای پنل روی 127.0.0.1:{chosen_port}")
    uvicorn.run(app, host="127.0.0.1", port=chosen_port, log_level="info")
