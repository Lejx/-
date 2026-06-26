from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation


SELECTIONS = {
    "WK1_2.pdf": "3B 5B 6T 6B 7T 9T 10B 12T 13T 13B 14T 14B 15T",
    "WK2.pdf": "26B 27T 27B 28T 28B 29T 29B",
    "WK3-2.pdf": "4B 5T 5B 6T 6B 7T 7B 8T 8B 49B 50T",
    "WK4-1.pdf": "6B 7T",
    "WK5.pdf": "7T 7B 9T 9B 11T 11B 12B 13T 13B 14T 16T 16B 17T 21B 22T 22B 23T 23B 25T 25B",
    "WK6.pdf": "3B 5T 9B 12T 14T 14B 15T 15B",
    "WK7.pdf": "10T 11B 12B",
    "WK8.pdf": "1B 3B 4T 4B 5T 5B 7T 7B 9T",
    "WK10-1.pdf": "3T 3B",
    "WK10-2.pdf": "9T 9B 10T 10B 11T 11B 12T",
    "WK12.pdf": "4T 4B 6B 7T",
    "WK13.pdf": "10T 10B 11B 12T 12B 13T 13B 14T 14B 15T 15B 16T 16B 17T",
    "WK14.pdf": "8T 8B 9T",
}


def add_half(writer, source_page, half):
    width = float(source_page.mediabox.width)
    height = float(source_page.mediabox.height)
    output = writer.add_blank_page(width=width, height=height / 2)
    if half == "T":
        output.merge_transformed_page(
            source_page, Transformation().translate(0, -height / 2)
        )
    else:
        output.merge_page(source_page)


writer = PdfWriter()
for filename, refs_text in SELECTIONS.items():
    reader = PdfReader(filename)
    for ref in refs_text.split():
        page_number = int(ref[:-1])
        add_half(writer, reader.pages[page_number - 1], ref[-1])

output_path = Path("自控例题.pdf")
with output_path.open("wb") as output_file:
    writer.write(output_file)

print(f"Wrote {output_path} with {len(writer.pages)} pages")
