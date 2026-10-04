// Make a logo's solid background transparent: near-white pixels connected to the image edge are cleared
// (flood fill from the border, so white inside the crest stays), with a soft edge, then the result is scaled to 128px.
// Works from ESPN's 500px original for a clean edge. Needs Playwright's Chromium (used for canvas).
//
//   node scripts/logos/clear_bg.js 17828-d 17850-d ...     # file names under src/logos, without .png
//
// fetch.js leaves these files alone (CLEARED there), so a refresh doesn't bring the white squares back.
const fs = require('fs'), path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT || '/opt/node22/lib/node_modules/playwright');
const OUT = path.resolve(__dirname, '../../src/logos');

(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  for (const name of process.argv.slice(2)) {
    const [id, v] = name.split('-'), url = `https://a.espncdn.com/i/teamlogos/soccer/${v === 'd' ? '500-dark' : '500'}/${id}.png`;
    const buf = Buffer.from(await (await fetch(url)).arrayBuffer());
    const png = await p.evaluate(async b64 => {
      const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
      const W = img.width, H = img.height, c = document.createElement('canvas'); c.width = W; c.height = H;
      const x = c.getContext('2d'); x.drawImage(img, 0, 0);
      const im = x.getImageData(0, 0, W, H), d = im.data;
      const far = i => 255 * 3 - d[i] - d[i + 1] - d[i + 2];          // 0 = pure white
      const seen = new Uint8Array(W * H), st = [];
      for (let i = 0; i < W; i++) st.push(i, (H - 1) * W + i);
      for (let j = 0; j < H; j++) st.push(j * W, j * W + W - 1);
      while (st.length) {
        const q = st.pop(); if (seen[q]) continue; seen[q] = 1;
        const o = q * 4, f = far(o);
        if (d[o + 3] < 20 || f < 60) {                                   // background: clear and keep spreading
          d[o + 3] = 0;
          const i = q % W, j = (q - i) / W;
          if (i > 0) st.push(q - 1); if (i < W - 1) st.push(q + 1); if (j > 0) st.push(q - W); if (j < H - 1) st.push(q + W);
        } else if (f < 160) d[o + 3] = Math.round(d[o + 3] * (f - 60) / 100);   // anti-aliased rim: fade
      }
      x.putImageData(im, 0, 0);
      const s = 128 / Math.max(W, H), o = document.createElement('canvas'); o.width = Math.round(W * s); o.height = Math.round(H * s);
      const y = o.getContext('2d'); y.imageSmoothingQuality = 'high'; y.drawImage(c, 0, 0, o.width, o.height);
      return o.toDataURL('image/png').split(',')[1];
    }, buf.toString('base64'));
    fs.writeFileSync(path.join(OUT, name + '.png'), Buffer.from(png, 'base64'));
    console.log('cleared', name);
  }
  await b.close();
})();
