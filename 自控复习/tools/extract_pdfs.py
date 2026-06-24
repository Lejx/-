from __future__ import annotations

import json
import re
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_extracted"


def flatten_outline(items, level=0):
    rows = []
    for item in items:
        if isinstance(item, list):
            rows.extend(flatten_outline(item, level + 1))
            continue
        title = getattr(item, "title", str(item))
        rows.append({"level": level, "title": title})
    return rows


def main() -> None:
    OUT.mkdir(exist_ok=True)
    manifest = []
    for pdf_path in sorted(ROOT.glob("*.pdf")):
        reader = PdfReader(pdf_path)
        page_texts = []
        for page_no, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            page_texts.append(f"\n\n===== PAGE {page_no} =====\n{text}")
        out_path = OUT / f"{pdf_path.stem}.txt"
        out_path.write_text("".join(page_texts), encoding="utf-8")
        try:
            outline = flatten_outline(reader.outline)
        except Exception:
            outline = []
        manifest.append(
            {
                "file": pdf_path.name,
                "pages": len(reader.pages),
                "characters": sum(len(text) for text in page_texts),
                "outline": outline,
            }
        )
    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
