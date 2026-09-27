import pdfplumber, re, json, datetime
from zoneinfo import ZoneInfo
P='/mnt/user-data/uploads/Premier_League_Scores___Fixtures___FBref_com.pdf'
MAP={'Manchester Utd':'Manchester United','Nottingham':'Nottingham Forest','Newcastle':'Newcastle United','Tottenham':'Tottenham Hotspur'}
NAMES=['Arsenal','Coventry City','Hull City','Manchester Utd','Ipswich Town','Sunderland','Nottingham','Leeds United','Everton','Crystal Palace','Brentford','Tottenham',
 'Manchester City','Bournemouth','Brighton','Aston Villa','Newcastle','Liverpool','Fulham','Chelsea']
ALT='|'.join(re.escape(n) for n in sorted(NAMES,key=len,reverse=True))
rows=[]
with pdfplumber.open(P) as pdf:
    for p in pdf.pages:
        W=p.extract_words(); groups=[]
        for w in sorted(W,key=lambda w:w['top']):
            if groups and abs(w['top']-groups[-1][0])<=4: groups[-1][1].append(w)
            else: groups.append([w['top'],[w]])
        for _,ws in groups:
            ws=sorted(ws,key=lambda w:w['x0']); txt=' '.join(w['text'] for w in ws)
            m=re.match(r'^(\d+) (Mon|Tue|Wed|Thu|Fri|Sat|Sun) (20\d\d-\d\d-\d\d) (\d\d:\d\d) \((\d\d:\d\d)\)',txt)
            if not m: continue
            mm=re.search('('+ALT+r') (?:(\d+)–(\d+) )?('+ALT+')',txt)
            if not mm: print('NOMATCH',txt); continue
            h,a=MAP.get(mm.group(1),mm.group(1)),MAP.get(mm.group(4),mm.group(4))
            uk=datetime.datetime.fromisoformat(m.group(3)+'T'+m.group(4)).replace(tzinfo=ZoneInfo('Europe/London'))
            rows.append(dict(wk=int(m.group(1)),date=m.group(3),utc=uk.astimezone(ZoneInfo('UTC')).strftime('%Y-%m-%dT%H:%MZ'),h=h,a=a,
                             hs=int(mm.group(2)) if mm.group(2) else None,as_=int(mm.group(3)) if mm.group(3) else None))
print(len(rows), sum(1 for r in rows if r['hs'] is not None))
json.dump(rows,open('/home/claude/w/epl2/rows.json','w'))
