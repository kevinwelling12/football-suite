"""Fold the minor penalties into the factors (Kevin, 2026-10-02). Run once.
Multi-club and overspend -> Ownership, franchise -> History, betting-owner and 'Other' conduct items -> Values. The points
convert at the factor's weight (1 Ownership point = 1.11 Affinity, History 1.78, Values 2.89); what Ownership or History
cannot absorb (already 0) spills into Values. Hard lines (racism, state, fan violence, private equity, buyouts, Super
League, government) stay as adjustments. The Republic link moves to the connection items (big4.py)."""
import pathlib, re
root = pathlib.Path(__file__).resolve().parents[2]
PER = {'O': 1.0 / 0.9, 'H': 1.6 / 0.9, 'V': 2.6 / 0.9}
IDX = {'C': 0, 'V': 1, 'H': 2, 'O': 3}
WHERE = {'Multi-club': 'O', 'Overspend': 'O', 'Franchise': 'H', "Owner's fortune from sports betting": 'V', 'Other': 'V'}
NUM = r'(-?\d+(?:\.\d+)?)'
log = []
for path in ['scripts/affinity/scores.py', 'scripts/importers/build_usl.py']:
    p = root / path; src = p.read_text()
    def sub(m):
        q, name = m.group(1), m.group(2)
        v = [float(x) for x in m.group(3, 4, 5, 6)]; adj = float(m.group(8)); note = m.group(9)
        keep, folded = [], []
        for part in [x.strip() for x in note.split(';') if x.strip()]:
            mm = re.match(r'(.*?)\s*([+-]\d+(?:\.\d+)?)$', part)
            lab = mm.group(1) if mm else None
            if lab in WHERE or lab == 'Republic link':
                pts = float(mm.group(2)); adj -= pts
                if lab == 'Republic link': folded.append(f'{part} -> connection items'); continue
                f = WHERE[lab]; d = pts / PER[f]; i = IDX[f]
                take = max(d, -v[i]); v[i] = round(v[i] + take, 1); rest = (d - take) * PER[f]
                txt = f'{part} -> {"Ownership History Values".split()[" OHV".index(f) - 1]} {take:+.1f}'
                if rest < -0.05:
                    dv = max(rest / PER['V'], -v[1]); v[1] = round(v[1] + dv, 1); txt += f', Values {dv:+.1f}'
                folded.append(txt)
            else:
                keep.append(part)
        if not folded: return m.group(0)
        log.append((name, folded))
        note2 = '; '.join(keep + ['Folded 2026-10-02: ' + ', '.join(folded)])
        fmt = lambda x: str(int(x)) if x == int(x) else str(round(x, 1))
        return f'{q}{name}{q}:({",".join(fmt(x) for x in v)},{m.group(7)},{fmt(round(adj, 1))},"{note2}")'
    src = re.sub(r"""(['"])([^'"]+)\1:\(""" + NUM + ',' + NUM + ',' + NUM + ',' + NUM + ',' + NUM + ',' + NUM + r',"([^"]*)"\)', sub, src)
    p.write_text(src)
for n, f in log: print(n, '|', '; '.join(f))
print(len(log), 'clubs')
