import json, sys, difflib, re, datetime
key, fn = sys.argv[1], sys.argv[2]
ALIAS=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
names, body = open(fn).read().strip().split('\n')
names=names.split('|'); B=1767225600
D=json.load(open('data/suite_data.json')); L=D[key]; T=L['teams']
def norm(s): return re.sub(r'[^a-z0-9]','',s.lower().replace('fc','').replace('ac','').replace('cf',''))
m={}
for n in names:
    if n in ALIAS: m[n]=[i for i,t in enumerate(T) if t['name']==ALIAS[n]][0]; continue
    best=max(range(len(T)),key=lambda i: max(difflib.SequenceMatcher(None,norm(n),norm(T[i]['name'])).ratio(),difflib.SequenceMatcher(None,norm(n),norm(T[i].get('short',''))).ratio()))
    m[n]=best
inv={}
for n,i in m.items(): inv.setdefault(i,[]).append(n)
dups={T[i]['name']:v for i,v in inv.items() if len(v)>1}
if dups: print('DUPLICATE MAP',dups); sys.exit(1)
pair={(f[2],f[3]):i for i,f in enumerate(L['fixtures'])}
kick=L.setdefault('kick',{}); res=[];dch=[];tch=0;newt=0;miss=[]
for r in body.split(';'):
    p=r.split(','); when,h,a=p[0],names[int(p[1],36)],names[int(p[2],36)]
    k=(m[h],m[a])
    if k not in pair: miss.append((h,a)); continue
    i=pair[k]; f=L['fixtures'][i]
    if len(p)>3:
        hs,as_=map(int,p[3].split(':'))
        if f[4] is not None and (f[4],f[5])!=(hs,as_): res.append((T[f[2]]['short'],T[f[3]]['short'],f[4],f[5],hs,as_))
        if f[4] is None: res.append(('NEW',T[f[2]]['short'],T[f[3]]['short'],hs,as_))
        continue
    if f[4] is not None: continue
    if when.startswith('d'): continue
    ep=B+int(when,36)*60; dt=datetime.datetime.fromtimestamp(ep, datetime.timezone.utc).replace(tzinfo=None)
    iso=dt.strftime('%Y-%m-%dT%H:%MZ')
    old=kick.get(str(i))
    if not old or not old[1]: newt+=1
    elif old[0]!=iso: tch+=1
    kick[str(i)]=[iso,1]
    # date in venue-local terms: use kickoff local date approx (UTC-? ) keep europe date: UTC date is fine for Europe
    d=(dt+datetime.timedelta(hours=1)).strftime('%Y-%m-%d')
    if f[1]!=d: dch.append((T[f[2]]['short'],T[f[3]]['short'],f[1],d)); f[1]=d
json.dump(D,open('data/suite_data.json','w'),ensure_ascii=False,separators=(',',':'))
print(key,'result issues',res,'| date changes',len(dch),dch[:8],'| time changes',tch,'| newly timed',newt,'| unmatched',miss[:5])
