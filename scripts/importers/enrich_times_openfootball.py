import json, re, difflib, datetime, collections
from zoneinfo import ZoneInfo
D=json.load(open('app/suite_data.json'))
UTC=ZoneInfo('UTC')
def norm(s):
    s=s.lower().replace('&','and')
    for w in [' fc',' afc','afc ','fc ',' cf','cf ','1. ','ac ','as ','ss ','ssc ','us ','acf ','rc ','rcd ','cd ','ca ','ud ','sd ','sv ','vfb ','vfl ','tsg ','bsc ','sc ','ogc ','olympique ','stade ','ea ']:
        s=s.replace(w,' ')
    return re.sub(r'[^a-z0-9]','',s)
ALIAS={'Brighton':'Brighton & Hove Albion FC','Como':'Como 1907','Inter Milan':'FC Internazionale Milano','Parma':'Parma Calcio 1913','Brest':'Stade Brestois 29','Lyon':'Olympique Lyonnais','Rennes':'Stade Rennais FC 1901'}
def sim(a,b): return difflib.SequenceMatcher(None,norm(ALIAS.get(a,a)),norm(b)).ratio()
out={}
LEAGUES={'epl':('2026-27.en.1.json','Europe/London'),'esp':('2026-27.es.1.json','Europe/Madrid'),'ita':('2026-27.it.1.json','Europe/Rome'),
         'bl':('2026-27.de.1.json','Europe/Berlin'),'fra':('2026-27.fr.1.json','Europe/Paris'),'ch':('2026-27.en.2.json','Europe/London')}
for k,(fn,tz) in LEAGUES.items():
    om=json.load(open('/home/claude/data/'+fn))['matches']
    byround=collections.defaultdict(set)
    for x in om:
        if x.get('time') and not x.get('score'): byround[x['round']].add(x['time'])
    bydate=collections.defaultdict(list)
    for x in om: bydate[x['date']].append(x)
    T=D[k]['teams']; kick={}; hit=miss=0
    for i,f in enumerate(D[k]['fixtures']):
        if f[4] is not None: continue
        h,a=T[f[2]]['name'],T[f[3]]['name']
        cands=[x for dd in [f[1]] for x in bydate.get(dd,[])] or [x for x in om if not x.get('score')]
        best=max(cands,key=lambda x: sim(h,x['team1'])+sim(a,x['team2']))
        if sim(h,best['team1'])+sim(a,best['team2'])<1.3: miss+=1; continue
        hit+=1
        if not best.get('time'): continue
        conf = len(byround[best['round']])>1
        dt=datetime.datetime.fromisoformat(best['date']+'T'+best['time']).replace(tzinfo=ZoneInfo(tz)).astimezone(UTC)
        kick[i]=[dt.strftime('%Y-%m-%dT%H:%MZ'),1 if conf else 0]
    out[k]=kick; print(k,'matched',hit,'miss',miss,'times',len(kick),'confirmed',sum(v[1] for v in kick.values()))
# NWSL from FBref PDF: Pacific time = parenthetical if present else main
import pdfplumber
NAMES={'Wash. Spirit':'Washington Spirit','Current':'Kansas City Current','Royals':'Utah Royals','Reign':'Seattle Reign','SD Wave':'San Diego Wave','NC Courage':'North Carolina Courage','Bay FC':'Bay FC','Portland Thorns':'Portland Thorns','Gotham FC':'Gotham FC','Orlando Pride':'Orlando Pride','Chicago Stars':'Chicago Stars','Houston Dash':'Houston Dash','Racing Louisville':'Racing Louisville','Angel City FC':'Angel City FC','Boston Legacy':'Boston Legacy','Denver Summit':'Denver Summit'}
rows=json.load(open('nwsl_rows_final.json'))
pt_times=[]
with pdfplumber.open('/mnt/user-data/uploads/NWSL_Scores___Fixtures___FBref_com.pdf') as pdf:
    for p in pdf.pages:
        ws_all=sorted(p.extract_words(),key=lambda w:w['top']); groups=[]
        for w in ws_all:
            if groups and abs(w['top']-groups[-1][0])<=4: groups[-1][1].append(w)
            else: groups.append([w['top'],[w]])
        for _,ws in groups:
            ws=sorted(ws,key=lambda w:w['x0']); txt=' '.join(w['text'] for w in ws)
            m=re.match(r'^(\d+) (Mon|Tue|Wed|Thu|Fri|Sat|Sun) (2026-\d\d-\d\d)',txt)
            if not m: continue
            par=re.search(r'\((\d\d:\d\d)\)',txt); main=re.search(r'\b(\d\d:\d\d)\b',txt)
            pt_times.append((m.group(3), par.group(1) if par else (main.group(1) if main else None)))
assert len(pt_times)==len(rows)
T=D['nwsl']['teams']; idx={t['name']:i for i,t in enumerate(T)}; kick={}
key2t={(r[1],idx[NAMES[r[3]]],idx[NAMES[r[6]]]):pt_times[j][1] for j,r in enumerate(rows)}
for i,f in enumerate(D['nwsl']['fixtures']):
    if f[4] is not None: continue
    t=key2t.get((f[1],f[2],f[3]))
    if t:
        dt=datetime.datetime.fromisoformat(f[1]+'T'+t).replace(tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(UTC)
        kick[i]=[dt.strftime('%Y-%m-%dT%H:%MZ'),1]
out['nwsl']=kick; print('nwsl times',len(kick))
# MLS from Sports Media Watch (Eastern time)
MLS_ET="""2026-09-26|19:30|New York City|Atlanta
2026-09-26|19:30|Chicago Fire|Charlotte
2026-09-26|19:30|Cincinnati|Montr
2026-09-26|19:30|St. Louis|Red Bull
2026-09-26|19:30|Orlando|Philadelphia
2026-09-26|20:30|San Diego|Austin
2026-09-26|20:30|Los Angeles Football|Dallas
2026-09-26|20:30|Sporting|Houston
2026-09-26|20:30|Toronto|Nashville
2026-09-26|20:30|Minnesota|Seattle
2026-09-26|21:30|New England|Salt Lake
2026-09-26|22:30|Colorado|Galaxy
2026-09-26|22:30|Portland|San Jose
2026-09-26|22:30|D.C.|Vancouver
2026-09-27|19:00|Inter Miami|Columbus
2026-10-06|20:30|Vancouver|Chicago Fire
2026-10-10|13:00|Montr|Toronto
2026-10-10|14:30|New York City|Chicago Fire
2026-10-10|19:30|Cincinnati|Atlanta
2026-10-10|19:30|Dallas|Charlotte
2026-10-10|19:30|D.C.|Inter Miami
2026-10-10|19:30|Seattle|New England
2026-10-10|19:30|San Diego|Red Bull
2026-10-10|19:30|Columbus|Orlando
2026-10-10|19:30|Salt Lake|Philadelphia
2026-10-10|20:30|Nashville|Austin
2026-10-10|20:30|Portland|Sporting
2026-10-10|20:30|Houston|Minnesota
2026-10-10|21:30|San Jose|Colorado
2026-10-10|22:30|Vancouver|Los Angeles Football
2026-10-11|19:00|Galaxy|St. Louis
2026-10-14|19:30|New England|Cincinnati
2026-10-14|19:30|Charlotte|Columbus
2026-10-14|19:30|Red Bull|D.C.
2026-10-14|19:30|New York City|Inter Miami
2026-10-14|19:30|Atlanta|Montr
2026-10-14|19:30|Orlando|Toronto
2026-10-14|20:30|Philadelphia|Chicago Fire
2026-10-14|20:30|Seattle|Dallas
2026-10-14|20:30|Sporting|Nashville
2026-10-14|20:30|Vancouver|St. Louis
2026-10-14|21:30|Minnesota|Colorado
2026-10-14|21:30|San Jose|Salt Lake
2026-10-14|22:30|Portland|Galaxy
2026-10-14|22:30|Austin|Los Angeles Football
2026-10-14|22:30|Houston|San Diego
2026-10-17|14:30|Charlotte|Philadelphia
2026-10-17|16:30|St. Louis|Minnesota
2026-10-17|19:30|Inter Miami|Atlanta
2026-10-17|19:30|Chicago Fire|New England
2026-10-17|19:30|Toronto|Red Bull
2026-10-17|19:30|D.C.|Orlando
2026-10-17|20:30|Vancouver|Austin
2026-10-17|20:30|Dallas|Houston
2026-10-17|20:30|Salt Lake|Sporting
2026-10-17|22:30|San Diego|Galaxy
2026-10-17|22:30|Colorado|Portland
2026-10-17|22:30|Nashville|San Jose
2026-10-17|22:30|Montr|Seattle"""
T=D['mls']['teams']
def find(s): 
    c=[i for i,t in enumerate(T) if s.lower() in t['name'].lower()]
    assert len(c)==1,(s,[T[i]['name'] for i in c]); return c[0]
kick={}; datefix={}
un=[(i,f) for i,f in enumerate(D['mls']['fixtures']) if f[4] is None]
for line in MLS_ET.split('\n'):
    d,t,h,a=line.split('|'); hi,ai=find(h),find(a)
    m=[i for i,f in un if {f[2],f[3]}=={hi,ai} and f[1]==d] or [i for i,f in un if {f[2],f[3]}=={hi,ai}]
    if not m: print('MLS no fixture',h,a); continue
    dt=datetime.datetime.fromisoformat(d+'T'+t).replace(tzinfo=ZoneInfo('America/New_York')).astimezone(UTC)
    kick[m[0]]=[dt.strftime('%Y-%m-%dT%H:%MZ'),1]
    if D['mls']['fixtures'][m[0]][1]!=d: datefix[m[0]]=(D['mls']['fixtures'][m[0]][1],d); D['mls']['fixtures'][m[0]][1]=d
out['mls']=kick; print('mls times',len(kick),'date fixes',datefix)
for k,v in out.items(): D[k]['kick']={str(i):x for i,x in v.items()}
TV={'epl':'Peacock · NBC · USA Network','esp':'ESPN+ (select games on ESPN/ABC)','ita':'Paramount+ (select games on CBS; some free on CBS Sports Golazo)',
    'bl':'Fandango, free (marquee games on USA Network)','fra':'beIN SPORTS','ch':'Paramount+','nwsl':'Paramount+/CBS, ESPN, Prime Video, ION or Victory+',
    'mls':'Apple TV (select games on FOX/FS1)','ucl':'Paramount+ (select games on CBS)','unl':'FOX / FS1','cup':'Paramount+'}
for k in D: D[k]['tv']=TV[k]
json.dump(D,open('app/suite_data.json','w'),ensure_ascii=False,separators=(',',':'))
