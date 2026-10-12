// Prints the test's facts and trade-off pairs (from template.html) as JSON, so live.py scores exactly what the page asked.
const fs = require('fs');
const s = fs.readFileSync(__dirname + '/template.html', 'utf8');
const block = s.slice(s.indexOf('const CF = ['), s.indexOf('const SEVEN = '));
const out = new Function(block + '; return {CF, PF, CP, PP};')();
process.stdout.write(JSON.stringify(out));
