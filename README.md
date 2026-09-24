# Billing App — Billing & Inventory System

Desktop GUI app (tkinter + ttkbootstrap, "cosmo" theme). Billing, inventory, dashboard tabs; SQLite storage.

## Run

```bash
pip install ttkbootstrap pillow
python app.py
```

Requires Python 3.10+ with tkinter. Verified boot on Python 3.12 (Linux, xvfb, 2026-09-24) — window initializes with no errors.

Not a web/cloud app: it is a desktop tool. Package with PyInstaller for distribution.
