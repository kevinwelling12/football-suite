import json, math, re, datetime
from zoneinfo import ZoneInfo
D=json.load(open('app/suite_data.json')); old=D['unl']
ALIAS={'Czechia':'Czech Republic','Türkiye':'Turkey'}
rows=[l.strip().split('|') for l in open('unl2/fixtures.txt') if l.strip()]
groups={}
for d,g,h,s,a,t in rows:
    for n in (h,a): groups[ALIAS.get(n,n)]=g
pri_old=json.load(open('priors_unl.json'))
ELO={n:int(re.search(r'Elo (\d+)',v[2]).group(1)) for n,v in pri_old.items()}
ELO.update({'Switzerland':1870,'Scotland':1760,'Slovenia':1700,'North Macedonia':1560,'Ukraine':1810,'Hungary':1780,'Georgia':1700,'Northern Ireland':1600,
 'Austria':1880,'Republic of Ireland':1640,'Israel':1600,'Kosovo':1600,'Sweden':1760,'Poland':1780,'Romania':1730,'Bosnia and Herzegovina':1620,
 'Albania':1660,'Finland':1600,'Belarus':1470,'San Marino':900,'Armenia':1480,'Latvia':1330,'Montenegro':1560,'Cyprus':1370,
 'Slovakia':1730,'Kazakhstan':1420,'Faroe Islands':1380,'Moldova':1310,'Iceland':1600,'Bulgaria':1520,'Luxembourg':1450,'Estonia':1360,
 'Andorra':1130,'Malta':1230,'Gibraltar':1060,'Liechtenstein':1060,'Lithuania':1310,'Azerbaijan':1420})
assert set(ELO)>=set(groups), set(groups)-set(ELO)
def pois(k,l): return math.exp(-l)*l**k/math.factorial(k)
def escore(s,base=1.35):
    lh,la=base*math.exp(s),base*math.exp(-s); W=D_=0
    for i in range(15):
        for j in range(15):
            p=pois(i,lh)*pois(j,la)
            if i>j: W+=p
            elif i==j: D_+=p
    return W+0.5*D_
def solve(E):
    lo,hi=-4,4
    for _ in range(60):
        m=(lo+hi)/2
        if escore(m)<E: lo=m
        else: hi=m
    return (lo+hi)/2
MEAN=1926
HAI_NEW={'Scotland':90,'Republic of Ireland':86,'Northern Ireland':84,'Iceland':88,'Faroe Islands':85,'Bosnia and Herzegovina':78,'Albania':76,'Kosovo':80,'Georgia':82,
 'Hungary':74,'Poland':72,'Ukraine':70,'Austria':68,'Switzerland':55,'Sweden':66,'Romania':70,'Slovenia':64,'North Macedonia':66,'Israel':50,'Finland':72,'Belarus':30,
 'San Marino':70,'Armenia':74,'Latvia':60,'Montenegro':68,'Cyprus':55,'Slovakia':64,'Kazakhstan':45,'Moldova':58,'Bulgaria':62,'Luxembourg':60,'Estonia':62,
 'Andorra':64,'Malta':70,'Gibraltar':72,'Liechtenstein':60,'Lithuania':66,'Azerbaijan':35}
BONUS={'Scotland':4.4,'Republic of Ireland':0.3,'Poland':0.6,'Lithuania':1.3,'Finland':0.3}
COL={'Switzerland':('SUI','#E30613'),'Scotland':('SCO','#3B6FD9'),'Slovenia':('SVN','#5BA3E0'),'North Macedonia':('MKD','#E30613'),'Ukraine':('UKR','#FFD500'),
 'Hungary':('HUN','#CE2939'),'Georgia':('GEO','#E6E6E6'),'Northern Ireland':('NIR','#2E9E5B'),'Austria':('AUT','#ED2939'),'Republic of Ireland':('IRL','#169B62'),
 'Israel':('ISR','#3B7CC4'),'Kosovo':('KOS','#4A7FD6'),'Sweden':('SWE','#FECC02'),'Poland':('POL','#DC143C'),'Romania':('ROU','#FCD116'),'Bosnia and Herzegovina':('BIH','#3B6FD9'),
 'Albania':('ALB','#E41E20'),'Finland':('FIN','#5B8FD9'),'Belarus':('BLR','#C8313E'),'San Marino':('SMR','#5EB6E4'),'Armenia':('ARM','#F2A800'),'Latvia':('LVA','#9E3039'),
 'Montenegro':('MNE','#D3AE3B'),'Cyprus':('CYP','#4A90D9'),'Slovakia':('SVK','#3B7CC4'),'Kazakhstan':('KAZ','#00AFCA'),'Faroe Islands':('FRO','#4A90D9'),'Moldova':('MDA','#FFD200'),
 'Iceland':('ISL','#3B6FD9'),'Bulgaria':('BUL','#00966E'),'Luxembourg':('LUX','#00A1DE'),'Estonia':('EST','#4891D9'),'Andorra':('AND','#D0103A'),'Malta':('MLT','#CF142B'),
 'Gibraltar':('GIB','#DA000C'),'Liechtenstein':('LIE','#3B6FD9'),'Lithuania':('LTU','#FDB913'),'Azerbaijan':('AZE','#00B5E2')}
oldT={t['name']:t for t in old['teams']}
names=sorted(groups)
T=[]
for n in names:
    E=1/(1+10**(-(ELO[n]-MEAN)/400)); s=solve(E)
    if n in oldT:
        t=dict(oldT[n]); t['group']=groups[n]
    else:
        ab,co=COL[n]; t=dict(name=n,base=HAI_NEW[n],bonus=BONUS.get(n,0),region='',drivers='First-draft HAI score for a League '+groups[n][0]+' nation.',abbr=ab,color=co,group=groups[n])
    t['pa'],t['pd']=round(math.exp(s),3),round(math.exp(-s),3); t['elo']=ELO[n]
    t.setdefault('short',n)
    T.append(t)
idx={t['name']:i for i,t in enumerate(T)}
F=[];kick={}
for d,g,h,s,a,tm in rows:
    h,a=ALIAS.get(h,h),ALIAS.get(a,a)
    hs=as_=None
    if s!='v': hs,as_=map(int,s.split('-'))
    md=None
    F.append([None,d,idx[h],idx[a],hs,as_])
    dt=datetime.datetime.fromisoformat(d+'T'+tm).replace(tzinfo=ZoneInfo('Europe/Paris')).astimezone(ZoneInfo('UTC'))
    kick[str(len(F)-1)]=[dt.strftime('%Y-%m-%dT%H:%MZ'),1]
# matchday numbers from date windows
MD=[('2026-09-24','2026-09-26',1),('2026-09-27','2026-09-29',2),('2026-10-01','2026-10-03',3),('2026-10-04','2026-10-06',4),('2026-11-12','2026-11-14',5),('2026-11-15','2026-11-17',6)]
for f in F: f[0]=[m for a,b,m in MD if a<=f[1]<=b][0]
# League D: matchday numbering within 4 rounds is fine (by window)
D['unl']=dict(teams=T,fixtures=F,params=old['params'],kick=kick,tv=old['tv'])
json.dump(D,open('app/suite_data.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(T),len(F),sum(1 for f in F if f[4] is not None), [(t['name'],t['pa'],t['pd']) for t in T if t['name'] in ('Spain','San Marino','Scotland')])
