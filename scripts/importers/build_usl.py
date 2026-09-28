import json, datetime, sys
from zoneinfo import ZoneInfo
sys.path.insert(0,'/home/claude/w/hai2')
rows=json.load(open('usl/rows.json'))
FULL={"Lexington SC":("Lexington SC","West","LEX","#2E8BC0"),"Louisville City":("Louisville City FC","East","LOU","#8A4FC7"),"Charleston":("Charleston Battery","East","CHS","#FFD100"),
"Pittsburgh":("Pittsburgh Riverhounds","East","PIT","#FDB913"),"Monterey Bay":("Monterey Bay FC","West","MB","#2BB5E0"),"Oakland Roots":("Oakland Roots SC","West","OAK","#2E9E5B"),
"Sac Republic":("Sacramento Republic FC","West","SAC","#C8102E"),"FC Tulsa":("FC Tulsa","West","TUL","#F58025"),"Orange County":("Orange County SC","West","OC","#FF7A00"),
"LV Lights FC":("Las Vegas Lights FC","West","LV","#FF3EB5"),"San Antonio FC":("San Antonio FC","West","SA","#E03A3E"),"Phoenix Rising":("Phoenix Rising FC","West","PHX","#FF4B3E"),
"Sporting JAX":("Sporting JAX","East","JAX","#1FA8A0"),"Hartford Athletic":("Hartford Athletic","East","HFD","#2E8B57"),"El Paso":("El Paso Locomotive FC","West","ELP","#F58220"),
"CS Switchbacks":("Colorado Springs Switchbacks FC","West","COS","#3B82F6"),"B'ham Legion":("Birmingham Legion FC","East","BHM","#D6A62C"),"TB Rowdies":("Tampa Bay Rowdies","East","TBR","#22C55E"),
"Brooklyn FC":("Brooklyn FC","East","BKN","#9CA3AF"),"Indy Eleven":("Indy Eleven","East","IND","#E03A3E"),"Loudoun United":("Loudoun United FC","East","LDN","#EF4444"),
"Miami FC":("Miami FC","East","MIA","#2BA0E0"),"Rhode Island FC":("Rhode Island FC","East","RI","#F59E0B"),"Detroit City":("Detroit City FC","East","DET","#B83A5A"),
"New Mexico Utd":("New Mexico United","West","NM","#FACC15")}
SHORT={"Louisville City FC":"Louisville City","Charleston Battery":"Charleston","Pittsburgh Riverhounds":"Pittsburgh","Monterey Bay FC":"Monterey Bay","Oakland Roots SC":"Oakland Roots",
"Sacramento Republic FC":"Sacramento Republic","Orange County SC":"Orange County","Las Vegas Lights FC":"Las Vegas Lights","Phoenix Rising FC":"Phoenix Rising","El Paso Locomotive FC":"El Paso",
"Colorado Springs Switchbacks FC":"Colorado Springs","Birmingham Legion FC":"Birmingham Legion","Tampa Bay Rowdies":"Tampa Bay","Loudoun United FC":"Loudoun United","Detroit City FC":"Detroit City"}
A={ # (Culture, Values, History, Ownership, Style, adj, note)
"Sacramento Republic FC":(9,8,6,8,5,0,""),"Louisville City FC":(8,7,6,7,7,0,""),"Detroit City FC":(9,9,5,8,6,0,""),"Charleston Battery":(5,6,7,5,7,0,""),
"Pittsburgh Riverhounds":(7,6,6,6,7,0,""),"Tampa Bay Rowdies":(6,6,7,5,7,0,""),"Indy Eleven":(7,6,5,4,5,0,""),"Hartford Athletic":(5,6,4,5,6,0,""),"Birmingham Legion FC":(4,6,3,5,3,0,""),
"Miami FC":(1,6,3,3,3,0,""),"Rhode Island FC":(7,6,2,6,5,0,""),"Loudoun United FC":(2,6,2,4,3,-4,"Multi-club -4"),"Brooklyn FC":(3,7,1,5,3,0,""),
"Sporting JAX":(2,7,1,5,2,0,""),"Lexington SC":(5,7,1,6,5,0,""),"Monterey Bay FC":(4,6,2,5,3,0,""),"Oakland Roots SC":(6,10,4,6,5,0,""),"FC Tulsa":(5,6,4,5,6,0,""),
"Orange County SC":(4,6,4,5,5,0,""),"Las Vegas Lights FC":(3,6,2,4,5,0,""),"San Antonio FC":(6,6,4,6,6,0,""),"Phoenix Rising FC":(5,5,4,5,5,0,""),"El Paso Locomotive FC":(5,6,3,5,6,0,""),
"Colorado Springs Switchbacks FC":(6,6,4,6,6,0,""),"New Mexico United":(8,8,4,7,6,0,"")}
W={'C':.26,'V':.28,'H':.16,'O':.12,'S':.08}
names=sorted(FULL[k][0] for k in FULL); idx={n:i for i,n in enumerate(names)}
teams=[]
for n in names:
    key=[k for k,v in FULL.items() if v[0]==n][0]; full,conf,ab,col=FULL[key]
    C,V,H,O,St,adj,note=A[n]
    base=max(0,round((W['C']*C+W['V']*V+W['H']*H+W['O']*O+W['S']*St)/0.90*10+adj,1))
    # Hometown rule: the club of the city you've lived in all your life gets the full club heritage cap (+4)
    bonus=4.0 if n=='Sacramento Republic FC' else 0
    teams.append(dict(name=n,short=SHORT.get(n,n),abbr=ab,color=col,group=conf,pa=1.0,pd=1.0,base=base,bonus=bonus,bonus0=bonus/0.4,
        region='Hometown club: Sacramento' if bonus else '',drivers='',hai=dict(C=C,V=V,H=H,O=O,S=St,adj=adj,note=note)))
key2idx={k:idx[v[0]] for k,v in FULL.items()}
fix=[];kick={}
for wk,d,pt,h,hs,as_,a in rows:
    fix.append([wk,d,key2idx[h],key2idx[a],hs,as_])
    if pt:
        dt=datetime.datetime.fromisoformat(d+'T'+pt).replace(tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(ZoneInfo('UTC'))
        kick[str(len(fix)-1)]=[dt.strftime('%Y-%m-%dT%H:%MZ'),1]
D=json.load(open('app/suite_data.json'))
params=dict(D['mls']['params']); params['zoneW']={}
D['usl']=dict(teams=teams,fixtures=fix,params=params,kick=kick,tv='ESPN Select (ESPN+)')
json.dump(D,open('app/suite_data.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(teams),len(fix),sorted([(t['base']+t['bonus'],t['name']) for t in teams],reverse=True)[:6])
