"""Download public academic sources and preserve Crossref metadata locally.

All files are kept inside the coursework project. Publisher paywalls are not
bypassed. The Modern Robotics preprint is for personal use only, not rehosting.
"""
import json
import pathlib
import urllib.request
import time

ROOT = pathlib.Path(__file__).resolve().parent
ITEMS = [
    ('images/Five_bar_mechanism_I_Elgamal_2020.png', 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Five_bar_mechanism.png'),
    ('papers/Asada_2005_Ch3_Robot_Mechanisms.pdf', 'https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/5c238d7e3445337ed40d4af83d9d2239_chapter3.pdf'),
    ('papers/Asada_2005_Ch4_Planar_Kinematics.pdf', 'https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/c8828a16e71c246b78461dd0596b983f_chapter4.pdf'),
    ('papers/Asada_2005_Ch5_Differential_Motion.pdf', 'https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/d6edf8a76e7674076c6fd5c09dedbed3_chapter5.pdf'),
    ('papers/Asada_2005_Ch7_Dynamics.pdf', 'https://ocw.mit.edu/courses/2-12-introduction-to-robotics-fall-2005/c7caaa2376b8ec01e270328a3b80b029_chapter7.pdf'),
    ('papers/Lynch_Park_2017_Modern_Robotics_personal_use_preprint.pdf', 'https://hades.mech.northwestern.edu/images/7/7f/MR.pdf'),
    ('metadata/Wikimedia_Five_bar_license.html', 'https://commons.wikimedia.org/wiki/File:Five_bar_mechanism.png'),
    ('metadata/Tedrake_acrobot.html', 'https://underactuated.csail.mit.edu/acrobot.html'),
    ('papers/Yoshikawa_1985_Manipulability_author_copy.pdf', 'https://tsuneo-yoshikawa.my.coocan.jp/PDF-of-Papers/1985-EP2.pdf'),
]
DOIS = [
    '10.1016/j.mechmachtheory.2005.05.004',
    '10.1109/70.56660',
    '10.1115/1.4011045',
    '10.1115/1.3149599',
    '10.1177/027836498500400201',
]


def download(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 RobotDynamics-Coursework/1.0'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)


def main():
    for path, url in ITEMS:
        try:
            if (ROOT / path).exists():
                print('PRESENT', path, flush=True)
                continue
            data = download(url)
            dest = ROOT / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            print(path, len(data), flush=True)
        except Exception as exc:
            print('ERROR', path, type(exc).__name__, str(exc), flush=True)
    for doi in DOIS:
        try:
            dest = ROOT / 'metadata' / ('crossref_' + doi.replace('/', '_') + '.json')
            if dest.exists():
                print('PRESENT DOI', doi, flush=True)
                continue
            data = download('https://api.crossref.org/works/' + doi)
            dest.write_bytes(data)
            m = json.loads(data)['message']
            print('DOI', doi, json.dumps({k: m.get(k) for k in ['title', 'author', 'published', 'volume', 'issue', 'page', 'container-title']}, ensure_ascii=False), flush=True)
        except Exception as exc:
            print('ERROR DOI', doi, str(exc), flush=True)


if __name__ == '__main__':
    main()
