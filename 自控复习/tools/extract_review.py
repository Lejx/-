from pypdf import PdfReader
import os, glob

pdf_dir = '复习资料'
out_dir = '_extracted/复习资料'
os.makedirs(out_dir, exist_ok=True)

for pdf_path in sorted(glob.glob(os.path.join(pdf_dir, '*.pdf'))):
    fname = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(out_dir, fname + '.txt')
    try:
        reader = PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            pages.append(f'===== PAGE {i+1} =====\n{text}')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(pages))
        print(f'OK: {fname} ({len(reader.pages)} pages)')
    except Exception as e:
        print(f'FAIL: {fname}: {e}')
