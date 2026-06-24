from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_extracted" / "textbook_pages"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(ROOT / "教科书.pdf")
    page_paths = []
    for page_no, page in enumerate(reader.pages, start=1):
        images = list(page.images)
        if not images:
            continue
        image = images[0].image.convert("RGB")
        page_path = OUT / f"page-{page_no:02d}.jpg"
        image.save(page_path, quality=90)
        page_paths.append((page_no, page_path))

    thumb_w, thumb_h = 248, 351
    cols, rows_per_sheet = 4, 3
    for sheet_no, start in enumerate(range(0, len(page_paths), cols * rows_per_sheet), 1):
        group = page_paths[start : start + cols * rows_per_sheet]
        sheet = Image.new("RGB", (cols * thumb_w, rows_per_sheet * (thumb_h + 28)), "white")
        draw = ImageDraw.Draw(sheet)
        for index, (page_no, page_path) in enumerate(group):
            image = Image.open(page_path).convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8))
            x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
            y = (index // cols) * (thumb_h + 28)
            sheet.paste(image, (x, y))
            draw.text((x + 4, y + thumb_h + 2), f"Page {page_no}", fill="black")
        sheet.save(OUT / f"contact-{sheet_no:02d}.jpg", quality=92)


if __name__ == "__main__":
    main()
