"""Render all final pages and record inspectable structural PDF checks."""
from pathlib import Path
import hashlib
import json
import re
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / 'outputs/机器人动力学基础结课报告_张子安琪_2024079102.pdf'
QA = ROOT / 'outputs/validation'
PAGES = QA / 'pdf_pages'

def main():
    PAGES.mkdir(parents=True, exist_ok=True)
    document = fitz.open(PDF)
    expected_pages = {f'page_{i+1:02d}.png' for i in range(len(document))}
    # Remove obsolete renderer outputs when the report becomes shorter.
    for stale in PAGES.glob('page_*.png'):
        if stale.name not in expected_pages:
            stale.unlink()
    for stale in QA.glob('contact_*.jpg'):
        stale.unlink()
    rows = []
    for index, page in enumerate(document):
        path = PAGES / f'page_{index+1:02d}.png'
        pix = page.get_pixmap(matrix=fitz.Matrix(1.65, 1.65), alpha=False)
        pix.save(path)
        text = page.get_text()
        outside = []
        for b in page.get_text('dict')['blocks']:
            for line in b.get('lines', []):
                for span in line['spans']:
                    x0,y0,x1,y1 = span['bbox']
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        outside.append({'text':span['text'],'bbox':span['bbox']})
        rows.append({'page':index+1, 'text_characters':len(text), 'out_of_page_text':outside,
                     'image':str(path.relative_to(ROOT))})
    # Contact sheets aid occupancy review; full-resolution images remain available.
    for start in range(0, len(document), 12):
        sheet = Image.new('RGB', (4*300,3*445), '#dce1e7')
        for offset in range(min(12,len(document)-start)):
            im=Image.open(PAGES / f'page_{start+offset+1:02d}.png').convert('RGB')
            im.thumbnail((280,405))
            x=(offset%4)*300+10; y=(offset//4)*445+25
            sheet.paste(im,(x,y))
            ImageDraw.Draw(sheet).text((x,y-18),f'PDF page {start+offset+1}',fill='black')
        sheet.save(QA / f'contact_{start+1:02d}_{min(start+12,len(document)):02d}.jpg',quality=92)
    log=(ROOT/'outputs/latex_build/main.log').read_text(encoding='utf-8',errors='replace')
    errors=[x for x in log.splitlines() if re.search(r'Overfull|Underfull|Warning|undefined|Missing character',x)]
    combined='\n'.join(p.get_text() for p in document)
    reference_start = next((i for i,p in enumerate(document)
                            if re.match(r'^\s*参考文献\s*\n', p.get_text())), None)
    reference_text = '' if reference_start is None else '\n'.join(
        document[i].get_text() for i in range(reference_start, len(document)))
    reference_numbers = sorted({int(n) for n in re.findall(r'(?m)^\[(\d+)\]', reference_text)})
    checks={'pdf':str(PDF.relative_to(ROOT)), 'page_count':len(document), 'size_bytes':PDF.stat().st_size,
        'sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(), 'compile_warnings':errors,
        'metadata':document.metadata, 'has_student_name':'张子安琪' in combined,
        'has_student_id':'2024079102' in combined, 'has_correct_class':'20240414' in combined,
        'has_date':'2026.10.25' in combined, 'has_sample_id':'2022041401' in combined,
        'has_unresolved_references':'??' in combined,
        'has_appendix':'附录' in combined,
        'references_start_page':None if reference_start is None else reference_start+1,
        'reference_numbers':reference_numbers,
        'references_found':len(reference_numbers),
        'pages':rows}
    (QA/'pdf_structural_checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in checks.items() if k!='pages'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
