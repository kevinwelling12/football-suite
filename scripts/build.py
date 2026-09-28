"""Build the app into one self-contained HTML page.

  python3 scripts/build.py            # web target  -> dist/web/index.html  (GitHub Pages; Firebase sync)
  python3 scripts/build.py --claude   # claude.ai   -> dist/football_suite.html (artifact runtime db; no external scripts)
"""
import json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent.parent
src = root / 'src'
FIREBASE_SDK = '10.12.2'
claude = '--claude' in sys.argv

html = (src / 'index.template.html').read_text()
app = (src / 'app.js').read_text().replace('/*__DATA__*/', (root / 'data' / 'suite_data.json').read_text())
head = ''
if not claude:
    sdk = ''.join(f'<script src="https://www.gstatic.com/firebasejs/{FIREBASE_SDK}/firebase-{m}-compat.js"></script>\n'
                  for m in ('app', 'auth', 'firestore'))
    seed = {p.stem: json.loads(p.read_text()) for p in sorted((root / 'user-data').glob('*.json'))}
    head = (sdk + '<script>' + (src / 'firebase-config.js').read_text() + '</script>\n'
            + '<script>window.SEED = ' + json.dumps(seed, ensure_ascii=False, separators=(',', ':')) + ';</script>')
# Icons: the web build links files copied next to the page (iOS needs a real apple-touch-icon file);
# the claude.ai build inlines the small favicon.
icons = src / 'icons'
if claude:
    import base64
    icon_tags = '<link rel="icon" type="image/png" href="data:image/png;base64,' + base64.b64encode((icons / 'favicon-32.png').read_bytes()).decode() + '">'
else:
    icon_tags = ('<link rel="icon" type="image/svg+xml" href="icon.svg">\n<link rel="icon" type="image/png" sizes="32x32" href="favicon-32.png">\n'
                 '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n<meta name="apple-mobile-web-app-title" content="Football">\n'
                 '<meta name="theme-color" content="#050408">')
out = (html.replace('<!--__ICONS__-->', icon_tags).replace('/*__WEB_HEAD__*/', head)
           .replace('/*__CSS__*/', (src / 'styles.css').read_text())
           .replace('/*__CONFIG__*/', (src / 'config.js').read_text())
           .replace('/*__MODEL__*/', (src / 'model.js').read_text())
           .replace('/*__APP__*/', app))
dest = root / 'dist' / ('football_suite.html' if claude else 'web/index.html')
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(out)
if not claude:
    import shutil
    for f in ('icon.svg', 'favicon-32.png', 'apple-touch-icon.png'): shutil.copyfile(icons / f, dest.parent / f)
print(f'wrote {dest.relative_to(root)} ({len(out):,} bytes)')
