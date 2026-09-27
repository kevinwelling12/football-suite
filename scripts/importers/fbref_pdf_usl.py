import pdfplumber, re, json
P='/mnt/user-data/uploads/USL_Championship_Scores___Fixtures___FBref_com.pdf'
NAMES=["Lexington SC","Louisville City","Charleston","Pittsburgh","Monterey Bay","Oakland Roots","Sac Republic","FC Tulsa","Orange County","LV Lights FC","San Antonio FC","Phoenix Rising","Sporting JAX","Hartford Athletic","El Paso","CS Switchbacks","B'ham Legion","TB Rowdies","Brooklyn FC","Indy Eleven","Loudoun United","Miami FC","Rhode Island FC","Detroit City","New Mexico Utd"]
ALT='|'.join(re.escape(n) for n in sorted(NAMES,key=len,reverse=True))
rows=[]
with pdfplumber.open(P) as pdf:
    for p in pdf.pages:
        W=p.extract_words(keep_blank_chars=False, use_text_flow=False)
        hdr={w['text']:w for w in W if w['text'] in ('Home','Score','Away','Attendance')}
        if 'Home' in hdr: cols=hdr
        groups=[]
        for w in sorted(W,key=lambda w:w['top']):
            if groups and abs(w['top']-groups[-1][0])<=4: groups[-1][1].append(w)
            else: groups.append([w['top'],[w]])
        sx=cols['Score']['x0']; ax=cols['Away']['x0']; atx=cols['Attendance']['x0']
        for _,ws in groups:
            ws=sorted(ws,key=lambda w:w['x0']); txt=' '.join(w['text'] for w in ws)
            m=re.match(r'^(\d+) (Mon|Tue|Wed|Thu|Fri|Sat|Sun) (2026-\d\d-\d\d)',txt)
            if not m: continue
            mm=re.search('('+ALT+r') (?:(\d+–\d+) )?('+ALT+')',txt)
            if not mm: print('NO MATCH',txt); continue
            home,score,away=mm.group(1),mm.group(2),mm.group(3)
            par=re.search(r'\((\d\d:\d\d)\)',txt); main=re.search(r'\b(\d\d:\d\d)\b',txt)
            pt=par.group(1) if par else (main.group(1) if main else None)
            hs,as_=(map(int,score.split('–')) if score else (None,None))
            rows.append([int(m.group(1)),m.group(3),pt,home,hs,as_,away])
json.dump(rows,open('/home/claude/w/usl/rows.json','w'))
import collections
print(len(rows), 'played', sum(1 for r in rows if r[4] is not None))
names=collections.Counter([r[3] for r in rows]+[r[6] for r in rows]); print(len(names)); print(sorted(names.items()))
