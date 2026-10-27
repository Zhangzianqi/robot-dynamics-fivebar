"""Compile the report from its existing LaTeX source; all output stays local."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'outputs' / 'latex_build'
DESTINATION = ROOT / 'outputs' / '机器人动力学基础结课报告_张子安琪_2024079102.pdf'

def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    executable = shutil.which('xelatex')
    if not executable:
        raise SystemExit('XeLaTeX was not found. Install TeX Live with ctex support.')
    if not (ROOT / 'latex/assets/cover_background.pdf').exists():
        subprocess.run([sys.executable, str(ROOT / 'code/prepare_template.py')], check=True, cwd=ROOT)
    command = [executable, '-interaction=nonstopmode', '-halt-on-error', '-file-line-error',
               '-output-directory=' + str(BUILD), 'main.tex']
    for iteration in range(1, 4):
        result = subprocess.run(command, cwd=ROOT / 'latex', capture_output=True)
        (BUILD / f'xelatex_pass_{iteration}.txt').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            print(result.stdout.decode('utf-8', errors='replace')[-5000:])
            raise SystemExit(f'XeLaTeX pass {iteration} failed; inspect {BUILD}.')
    shutil.copy2(BUILD / 'main.pdf', DESTINATION)
    print(DESTINATION)

if __name__ == '__main__':
    main()
