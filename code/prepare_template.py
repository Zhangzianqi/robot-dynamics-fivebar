"""Retain the supplied Word cover appearance while replacing sample identity.

Input PDF is a read-only Word export of the original template.  The final text
is supplied by LaTeX; no source Word file is modified.
"""
from pathlib import Path
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / 'latex' / 'assets'
target.mkdir(parents=True, exist_ok=True)
source = fitz.open(ROOT / 'outputs/template_inspection/template.pdf')
out = fitz.open()
out.insert_pdf(source, from_page=0, to_page=0)
page = out[0]
# Remove only sample class, student ID, and name; retain table and other labels.
for rect in [(220, 382, 290, 403), (430, 382, 510, 403), (228, 417, 286, 437)]:
    page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
page.apply_redactions(images=0, graphics=0)
out.save(target / 'cover_background.pdf', garbage=4, deflate=True)
print(target / 'cover_background.pdf')
