"""
Write frontend/public/data/careers.json: the career list (and South African
titles) the website falls back to while the Python engine is waking up.
Run after regenerating careers or SA titles:

    python scripts/export_careers_json.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.api.routes import careers_endpoint  # noqa: E402

OUT = ROOT.parent / "frontend" / "public" / "data" / "careers.json"


def main():
    data = careers_endpoint()
    OUT.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {len(data['careers'])} careers, {len(data['sa_titles'])} SA titles")


if __name__ == "__main__":
    main()
