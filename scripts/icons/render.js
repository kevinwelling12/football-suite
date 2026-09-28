// Renders src/icons/icon.svg to the PNG sizes the page links (apple-touch-icon 180 for the iOS home screen, favicon 32).
// Dev-only: node scripts/icons/render.js (needs Playwright). Commit the PNGs; build.py copies them to dist/web.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const dir = path.join(__dirname, '..', '..', 'src', 'icons');
(async () => {
  const svg = fs.readFileSync(path.join(dir, 'icon.svg'), 'utf8');
  const b = await chromium.launch();
  for (const [name, px] of [['apple-touch-icon.png', 180], ['favicon-32.png', 32]]) {
    const p = await b.newPage({ viewport: { width: px, height: px } });
    await p.setContent(`<style>html,body{margin:0}svg{display:block;width:${px}px;height:${px}px}</style>${svg}`);
    await p.screenshot({ path: path.join(dir, name), omitBackground: false });
    await p.close();
  }
  await b.close();
})();
