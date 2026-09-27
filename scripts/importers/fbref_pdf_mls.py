import pdfplumber, re, json, datetime
from zoneinfo import ZoneInfo
P='/mnt/user-data/uploads/Major_League_Soccer_Scores___Fixtures___FBref_com.pdf'
MAP={'St. Louis City':'St. Louis CITY SC','Charlotte':'Charlotte FC','Vancouver':'Vancouver Whitecaps FC','Real Salt Lake':'Real Salt Lake','FC Cincinnati':'FC Cincinnati',
'Atlanta Utd':'Atlanta United','LAFC':'Los Angeles Football Club','Inter Miami':'Inter Miami CF','Portland Timbers':'Portland Timbers','Columbus Crew':'Columbus Crew',
'SJ Earthquakes':'San Jose Earthquakes','Sporting KC':'Sporting Kansas City','San Diego FC':'San Diego FC','CF Montréal':'CF Montréal','Orlando City':'Orlando City',
'RB New York':'Red Bull New York','Nashville SC':'Nashville SC','NE Revolution':'New England Revolution','D.C. United':'D.C. United','Philadelphia':'Philadelphia Union',
'Houston':'Houston Dynamo FC','Chicago Fire':'Chicago Fire FC','Austin FC':'Austin FC','Minnesota Utd':'Minnesota United FC','FC Dallas':'FC Dallas','Toronto FC':'Toronto FC',
'LA Galaxy':'LA Galaxy','NYCFC':'New York City Football Club','Seattle Sounders':'Seattle Sounders FC','Colorado Rapids':'Colorado Rapids'}
ALT='|'.join(re.escape(n) for n in sorted(MAP,key=len,reverse=True))
rows=[];bad=[]
with pdfplumber.open(P) as pdf:
    for p in pdf.pages:
        W=p.extract_words(); groups=[]
        for w in sorted(W,key=lambda w:w['top']):
            if groups and abs(w['top']-groups[-1][0])<=4: groups[-1][1].append(w)
            else: groups.append([w['top'],[w]])
        for _,ws in groups:
            ws=sorted(ws,key=lambda w:w['x0']); txt=' '.join(w['text'] for w in ws)
            m=re.match(r'^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (2026-\d\d-\d\d) (\d\d:\d\d)(?: \((\d\d:\d\d)\))?',txt)
            if not m: continue
            mm=re.search('('+ALT+r') (?:(\d+)–(\d+) )?('+ALT+')',txt)
            if not mm: bad.append(txt); continue
            pt=m.group(4) or m.group(3)
            dt=datetime.datetime.fromisoformat(m.group(2)+'T'+pt).replace(tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(ZoneInfo('UTC'))
            rows.append(dict(date=m.group(2),utc=dt.strftime('%Y-%m-%dT%H:%MZ'),h=MAP[mm.group(1)],a=MAP[mm.group(4)],
                 hs=int(mm.group(2)) if mm.group(2) else None,as_=int(mm.group(3)) if mm.group(3) else None,txt=txt))
json.dump(rows,open('/home/claude/w/mls2/rows.json','w'))
print(len(rows),'played',sum(1 for r in rows if r['hs'] is not None),'unparsed',len(bad)); [print(' ',b) for b in bad]
