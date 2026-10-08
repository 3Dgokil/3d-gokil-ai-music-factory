import os, re, sqlite3
from collections import Counter
from datetime import datetime, timezone, timedelta
from googleapiclient.discovery import build
DB_NAME='youtube_research.db'
STOPWORDS={'the','and','for','with','this','that','from','your','you','are','was','will','into','about','best','new','full','official','video','live','mix','playlist','part','vol','version','2024','2025','2026','2027','dan','yang','untuk','dengan','dari','ini','itu','lagu','versi','terbaik'}

def get_youtube(api_key=None):
    key=api_key or os.environ.get('YOUTUBE_API_KEY')
    if not key: raise RuntimeError('YOUTUBE_API_KEY belum tersedia.')
    return build('youtube','v3',developerKey=key,cache_discovery=False)

def ensure_db():
    conn=sqlite3.connect(DB_NAME); cur=conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS videos(video_id TEXT PRIMARY KEY,title TEXT,channel_id TEXT,channel_name TEXT,published_at TEXT,description TEXT,thumbnail_url TEXT,views INTEGER DEFAULT 0,likes INTEGER DEFAULT 0,comments INTEGER DEFAULT 0,duration_seconds INTEGER DEFAULT 0,keyword TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS channels(channel_id TEXT PRIMARY KEY,channel_name TEXT,subscribers INTEGER DEFAULT 0,total_views INTEGER DEFAULT 0,video_count INTEGER DEFAULT 0,country TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT,video_id TEXT,recorded_at TEXT,views INTEGER DEFAULT 0,likes INTEGER DEFAULT 0,comments INTEGER DEFAULT 0)')
    conn.commit(); conn.close()

def parse_duration(s):
    m=re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '')
    return (int(m.group(1) or 0)*3600+int(m.group(2) or 0)*60+int(m.group(3) or 0)) if m else 0

def search_ids(yt,q,max_results,country,language,after):
    ids=[]; token=None
    while len(ids)<max_results:
        n=min(50,max_results-len(ids)); args=dict(part='snippet',q=q,type='video',maxResults=n,order='relevance')
        if token: args['pageToken']=token
        if country: args['regionCode']=country.upper()
        if language: args['relevanceLanguage']=language.lower()
        if after: args['publishedAfter']=after
        res=yt.search().list(**args).execute()
        for x in res.get('items',[]):
            vid=x.get('id',{}).get('videoId')
            if vid and vid not in ids: ids.append(vid)
        token=res.get('nextPageToken')
        if not token: break
    return ids

def score(item,channels):
    s=item['snippet']; st=item.get('statistics',{}); views=int(st.get('viewCount',0)); likes=int(st.get('likeCount',0)); comments=int(st.get('commentCount',0)); published=datetime.fromisoformat(s['publishedAt'].replace('Z','+00:00')); age=max(1,(datetime.now(timezone.utc)-published).total_seconds()/86400); ch=channels.get(s['channelId'],{}); subs=int(ch.get('subs',0)); vpd=views/age; eng=((likes+comments)/views*100) if views else 0; vs=views/subs if subs else 0
    velocity=30 if vpd>=100000 else 27 if vpd>=50000 else 24 if vpd>=25000 else 20 if vpd>=10000 else 16 if vpd>=5000 else 12 if vpd>=1000 else 8 if vpd>=500 else 4
    reach=25 if vs>=300 else 23 if vs>=150 else 20 if vs>=100 else 16 if vs>=50 else 12 if vs>=20 else 8 if vs>=10 else 4
    engagement=15 if eng>=3 else 13 if eng>=2 else 10 if eng>=1 else 7 if eng>=.5 else 4 if eng>=.2 else 1
    freshness=20 if age<=30 else 15 if age<=90 else 10 if age<=180 else 5 if age<=365 else 0
    small=10 if subs<=5000 else 8 if subs<=20000 else 5 if subs<=100000 else 2 if subs<=500000 else 0
    total=velocity+reach+engagement+freshness+small
    trend='VIRAL' if age<=60 and vpd>=10000 else 'GROWING' if age<=180 and vpd>=5000 else 'EVERGREEN' if age>=180 and vpd>=1000 else 'STABLE' if vpd>=1000 else 'WEAK'
    return {'id':item['id'],'title':s['title'],'channel':s['channelTitle'],'channel_id':s['channelId'],'published':s['publishedAt'],'views':views,'likes':likes,'comments':comments,'subs':subs,'age':age,'vpd':vpd,'eng':eng,'vs':vs,'score':total,'trend':trend,'duration':parse_duration(item.get('contentDetails',{}).get('duration',''))}

def tokens(title):
    t=re.sub(r'[^\w\s-]',' ',title.lower(),flags=re.UNICODE); return [x for x in t.split() if len(x)>=3 and x not in STOPWORDS and not x.isdigit()]
def pattern_extract(rows):
    uni,big=Counter(),Counter()
    for r in rows:
        w=max(1,r['score']); words=tokens(r['title'])
        for x in words: uni[x]+=w
        for a,b in zip(words,words[1:]): big[f'{a} {b}']+=w
    return uni.most_common(15),big.most_common(15)
def format_signal(r):
    d=r['duration']; return 'Shorts' if d<=60 else 'Short / medium' if d<=600 else 'Long-form' if d<=1800 else 'Long-form / compilation'
def make_dna(rows):
    return [{'title':r['title'],'channel':r['channel'],'trend':r['trend'],'score':r['score'],'format':format_signal(r),'pattern':'Strong reach relative to channel size' if r['vs']>=50 else 'Strong audience velocity' if r['vpd']>=5000 else 'Steady demand signal'} for r in rows[:8]]
def make_ideas(rows,niche):
    return [{'title':f'{niche.title()} — konsep original #{i}','why':f"Terinspirasi dari pola performa '{r['title']}', bukan menyalin isi.",'format':format_signal(r),'audience':'Target audience berdasarkan niche dan pola video teratas.','angle':'Ambil kebutuhan/tema umum dari pola tersebut, lalu ubah karakter, cerita, visual, struktur, dan eksekusi menjadi karya original.'} for i,r in enumerate(rows[:5],1)]

def run_research(keywords,country=None,language=None,max_results=30,days=365,api_key=None):
    ensure_db(); yt=get_youtube(api_key); queries=[x.strip() for x in keywords.split(',') if x.strip()]; after=(datetime.now(timezone.utc)-timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ') if days and days>0 else None
    ids=[]
    for q in queries: ids += search_ids(yt,q,max_results,country,language,after)
    ids=list(dict.fromkeys(ids))
    if not ids: raise RuntimeError('Tidak ada video ditemukan.')
    items=[]
    for i in range(0,len(ids),50): items += yt.videos().list(part='snippet,statistics,contentDetails',id=','.join(ids[i:i+50])).execute().get('items',[])
    chids=list(dict.fromkeys(x['snippet']['channelId'] for x in items)); chitems=[]
    for i in range(0,len(chids),50): chitems += yt.channels().list(part='snippet,statistics',id=','.join(chids[i:i+50])).execute().get('items',[])
    channels={}
    for c in chitems:
        st=c.get('statistics',{}); channels[c['id']]={'subs':int(st.get('subscriberCount',0)),'country':c.get('snippet',{}).get('country','')}
    rows=[score(x,channels) for x in items]; rows.sort(key=lambda x:x['score'],reverse=True)
    conn=sqlite3.connect(DB_NAME); cur=conn.cursor(); now=datetime.now(timezone.utc).isoformat()
    for r in rows:
        cur.execute('INSERT OR REPLACE INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(r['id'],r['title'],r['channel_id'],r['channel'],r['published'],'','',r['views'],r['likes'],r['comments'],r['duration'],','.join(queries)))
        cur.execute('INSERT OR REPLACE INTO channels(channel_id,channel_name,subscribers,country) VALUES(?,?,?,?)',(r['channel_id'],r['channel'],r['subs'],channels.get(r['channel_id'],{}).get('country','')))
        cur.execute('INSERT INTO snapshots(video_id,recorded_at,views,likes,comments) VALUES(?,?,?,?,?)',(r['id'],now,r['views'],r['likes'],r['comments']))
    conn.commit(); conn.close()
    terms,phrases=pattern_extract(rows); avg=sum(r['score'] for r in rows)/len(rows)
    summary={'avg_score':avg,'high':sum(r['score']>=60 for r in rows),'small_hits':sum(r['subs']<=20000 and r['vs']>=50 for r in rows)}
    import pandas as pd
    table=pd.DataFrame([{'Score':r['score'],'Trend':r['trend'],'Channel':r['channel'],'Title':r['title'],'Views':r['views'],'Subscribers':r['subs'],'View/Sub':round(r['vs'],1),'Views/Day':round(r['vpd']),'Engagement %':round(r['eng'],3),'Format':format_signal(r)} for r in rows[:50]])
    niche=' / '.join(queries)
    return {'videos':rows,'summary':summary,'table':table,'terms':terms,'phrases':phrases,'dna':make_dna(rows),'ideas':make_ideas(rows,niche)}

def youtube_client(api_key=None): return get_youtube(api_key)
def search_video_ids(yt,query,max_results,region_code=None,language=None,published_after=None,published_before=None): return search_ids(yt,query,max_results,region_code,language,published_after)[:max_results]
def fetch_video_details(yt,ids):
    out=[]
    for i in range(0,len(ids),50): out+=yt.videos().list(part='snippet,statistics,contentDetails',id=','.join(ids[i:i+50])).execute().get('items',[])
    return out
def fetch_channel_details(yt,channel_ids):
    out=[]; ids=list(dict.fromkeys(channel_ids))
    for i in range(0,len(ids),50): out+=yt.channels().list(part='snippet,statistics',id=','.join(ids[i:i+50])).execute().get('items',[])
    return out
def metrics(item,channel_map): return score(item,channel_map)
def research(keywords,country=None,language=None,max_per_keyword=50,published_after=None,published_before=None,api_key=None):
    keyword_text=', '.join(str(x).strip() for x in keywords if str(x).strip()) if isinstance(keywords,(list,tuple)) else str(keywords).strip()
    if not keyword_text: raise RuntimeError('Keyword/niche tidak boleh kosong.')
    days=365
    if published_after:
        try: days=max(1,int((datetime.now(timezone.utc)-datetime.fromisoformat(published_after.replace('Z','+00:00'))).total_seconds()/86400))
        except Exception: pass
    result=run_research(keyword_text,country=country,language=language,max_results=max(1,min(int(max_per_keyword),50)),days=days,api_key=api_key)
    if published_before:
        try:
            b=datetime.fromisoformat(published_before.replace('Z','+00:00')); result['videos']=[r for r in result['videos'] if datetime.fromisoformat(r['published'].replace('Z','+00:00'))<=b]
        except Exception: pass
    return result
