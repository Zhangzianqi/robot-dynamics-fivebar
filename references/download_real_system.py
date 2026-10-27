"""Preserve public primary sources identifying real five-bar drawing robots."""
from pathlib import Path
import re
import urllib.request
import time

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ('metadata/Quanser_2009_official_engineering_blog.html', 'https://quanser.blogspot.com/2009/04/mechatronics-supports-robotics.html'),
    ('metadata/Quanser_2013_manual_mirror.html', 'https://manualzz.com/doc/1358882/quanser-planar-robot-user-manual'),
    ('metadata/Quanser_2_DOF_Robot_official_product.html', 'https://www.quanser.com/products/2-dof-robot/'),
    ('images/Quanser_2009_2DOF_Planar_Robot_official_blog.jpg', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg4C9gT4LwBILpyUYrcrWHWrhKDNjMdA4bQRbcUzPC2LFikz7Io4aE6RP1kBZx82RgagQGejWvN-t-a2dMGyhyphenhyphenO_pXIhhFuO1YyQttfp3B-KrwzgC8XopOcYryW_b9kZJO2PPI4dMqdGBdD/s1600/293Q9207.jpg'),
]


def get(url):
    for i in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 RobotDynamics-Coursework/1.0'})
            with urllib.request.urlopen(req, timeout=25) as response:
                return response.read()
        except Exception:
            if i == 2:
                raise
            time.sleep(1)


def main():
    for path, url in SOURCES:
        try:
            dest = ROOT / path
            if not dest.exists():
                dest.write_bytes(get(url))
            print(path, dest.stat().st_size, flush=True)
            if dest.suffix == '.html' and 'blog' in path:
                html = dest.read_text(encoding='utf-8', errors='replace')
                urls = re.findall(r'(?:src|href)=[\"\']([^\"\']+)', html)
                for u in urls:
                    if re.search(r'(blogger|blogspot|googleusercontent)',u) and re.search(r'\.(jpe?g|png)(?:\?|$)',u,re.I):
                        print('BLOG_IMAGE',u,flush=True)
        except Exception as exc:
            print('ERROR', path, str(exc), flush=True)


if __name__ == '__main__':
    main()
