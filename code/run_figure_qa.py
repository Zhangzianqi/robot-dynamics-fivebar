"""Run portable figure source, panel, text-size and collision audits."""
from pathlib import Path
import subprocess
import sys
import json
import os

ROOT=Path(__file__).resolve().parents[1]
TOOLS=Path(__file__).resolve().parent/'qa_tools'
QA=ROOT/'outputs'/'validation'
QA.mkdir(parents=True,exist_ok=True)
summary=[]
env=dict(os.environ, PYTHONIOENCODING='utf-8')
for pdf in sorted((ROOT/'figures'/'generated').glob('*.pdf')):
    collision=subprocess.run([sys.executable,str(TOOLS/'audit_figure_collisions.py'),str(pdf),
       '--json-out',str(QA/(pdf.stem+'.collision.json'))],capture_output=True,text=True,encoding='utf-8',env=env)
    text=subprocess.run([sys.executable,str(TOOLS/'audit_pdf_text.py'),str(pdf),'--min-pt','5','--json'],
       capture_output=True,text=True,encoding='utf-8',env=env)
    summary.append({'file':str(pdf.relative_to(ROOT)),'collision_exit':collision.returncode,
       'collision_summary':collision.stdout,'text_exit':text.returncode,'text_audit':text.stdout})
    print(pdf.stem,'collision=',collision.returncode,'text=',text.returncode)
for filename in ['make_figures.py','scenario_sweeps.py']:
    source=subprocess.run([sys.executable,str(TOOLS/'validate_figure.py'),str(ROOT/'code'/filename),'--json'],
       capture_output=True,text=True,encoding='utf-8',env=env)
    (QA/(Path(filename).stem+'.source_audit.json')).write_text(source.stdout,encoding='utf-8')
(QA/'figure_qa_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
if any(x['collision_exit'] or x['text_exit'] for x in summary): raise SystemExit(1)
