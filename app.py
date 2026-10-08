import os,re,json,urllib.request
from datetime import datetime
from collections import defaultdict
import pandas as pd
import streamlit as st

st.set_page_config(page_title='3D GOKIL Music Factory',page_icon='🔥',layout='wide')
BRAND='3D GOKIL'
COUNTRIES={
'🇺🇸 United States':('US','en','English'),'🇮🇩 Indonesia':('ID','id','Bahasa Indonesia'),
'🇬🇧 United Kingdom':('GB','en','English'),'🇦🇺 Australia':('AU','en','English'),
'🇨🇦 Canada':('CA','en','English'),'🇩🇪 Germany':('DE','de','German'),
'🇯🇵 Japan':('JP','ja','Japanese'),'🇲🇾 Malaysia':('MY','ms','Bahasa Melayu'),'🌍 Global':(None,'en','English')}
THEMES={
'English':[
('❤️ Love & Relationships',['love songs','relationship songs','heartbreak songs']),('👨‍👩‍👧 Parents & Family',['songs about parents','family songs','mother father songs']),('💸 Money / Cost of Living',['cost of living songs','money problems songs','financial struggle songs']),('🌎 Society / Country Conditions',['social issues songs','society songs','social commentary music']),('💼 Work / Life Pressure',['work stress songs','working life songs','life struggle songs']),('🧠 Mental / Inner Struggle',['loneliness songs','anxiety songs','inner struggle songs'])],
'Bahasa Indonesia':[
('❤️ Cinta & Hubungan',['lagu cinta','lagu patah hati','lagu hubungan']),('👨‍👩‍👧 Orang Tua & Keluarga',['lagu tentang orang tua','lagu keluarga','lagu ibu ayah']),('💸 Uang / Biaya Hidup',['lagu masalah ekonomi','lagu tanggal tua','lagu biaya hidup']),('🌎 Sosial / Keadaan Negara',['lagu kritik sosial','lagu masalah sosial','lagu keadaan Indonesia']),('💼 Kerja / Tekanan Hidup',['lagu tekanan kerja','lagu pekerja','lagu tekanan hidup']),('🧠 Pergulatan Batin',['lagu kesepian','lagu keresahan','lagu perjuangan hidup'])],
'Bahasa Melayu':[
('❤️ Cinta & Hubungan',['lagu cinta','lagu patah hati','lagu hubungan']),('👨‍👩‍👧 Ibu Bapa & Keluarga',['lagu ibu bapa','lagu keluarga','lagu ibu ayah']),('💸 Duit / Kos Sara Hidup',['lagu masalah kewangan','kos sara hidup lagu','lagu susah hidup']),('🌎 Masyarakat / Negara',['lagu masalah sosial','lagu masyarakat','lagu negara']),('💼 Kerja / Tekanan Hidup',['lagu tekanan kerja','lagu kehidupan','lagu pekerja']),('🧠 Pergulatan Batin',['lagu kesunyian','lagu keresahan','lagu perjuangan hidup'])],
'German':[
('❤️ Liebe & Beziehungen',['Liebeslieder','Trennung Lieder','Beziehung Songs']),('👨‍👩‍👧 Eltern & Familie',['Lieder über Eltern','Familienlieder','Mutter Vater Lied']),('💸 Geld / Lebenshaltungskosten',['Lebenshaltungskosten Lied','Geldprobleme Songs','finanzielle Sorgen Lied']),('🌎 Gesellschaft / Land',['soziale Probleme Songs','Gesellschaft Lied','soziale Kritik Musik']),('💼 Arbeit / Lebensdruck',['Arbeitsstress Lied','Arbeitsleben Songs','Lebensdruck Lied']),('🧠 Innere Kämpfe',['Einsamkeit Lied','Angst Lied','innere Kämpfe Musik'])],
'Japanese':[
('❤️ 恋愛・失恋',['恋愛ソング','失恋ソング','恋愛 歌']),('👨‍👩‍👧 親・家族',['親への歌','家族の歌','母 父 歌']),('💸 お金・生活苦',['生活苦 歌','お金の悩み 歌','物価高 歌']),('🌎 社会・国の現状',['社会問題 歌','社会風刺 歌','日本 社会 歌']),('💼 仕事・人生のプレッシャー',['仕事 ストレス 歌','働く人生 歌','人生 苦労 歌']),('🧠 心の葛藤',['孤独 歌','不安 歌','心の葛藤 歌'])]}
GENRES={'ROCK / METAL':['Rock','Hard Rock','Heavy Metal','Alternative Rock','Metalcore'],'DANGDUT / KOPLO':['Dangdut','Koplo','Modern Dangdut','Rock Dangdut'],'ELECTRONIC / CYBER':['Electronic','EDM','Synthwave','Cyberpunk'],'NUSANTARA / TRADITIONAL':['Gamelan','Javanese Fusion','Suling Jawa','Indonesian Folk'],'POP / ALTERNATIVE':['Pop','Indie Pop','Alternative Pop','Lo-fi']}
GQ={'ROCK / METAL':['rock music','heavy metal music','hard rock music','metalcore music'],'DANGDUT / KOPLO':['dangdut music','koplo music','modern dangdut','rock dangdut'],'ELECTRONIC / CYBER':['electronic music','EDM music','synthwave music','cyberpunk music'],'NUSANTARA / TRADITIONAL':['gamelan music','Javanese gamelan','suling jawa','Indonesian folk music'],'POP / ALTERNATIVE':['pop music','indie pop music','alternative pop music','lofi music']}
ART={'CINEMATIC':'premium cinematic 3D social realism, dramatic lighting, deep depth, realistic character','SERIOUS':'serious grounded cinematic 3D realism, emotional character storytelling','SEMI-FUNNY':'serious realistic cinematic scene with one subtle intelligent visual joke, not cartoonish','GOKIL':'bold cinematic 3D visual metaphor, surprising but coherent, funny without childish parody','DARK / MYSTICAL':'dark mystical cinematic 3D realism, restrained symbolism, atmospheric fog'}
SPECTRUM=['BALOK','LINE','CLINE','P2P','FIRE','NONE']
try:
 import research
 RESEARCH_ERR=''
except Exception as e: research=None; RESEARCH_ERR=str(e)
try:
 if st.secrets.get('YOUTUBE_API_KEY'): os.environ['YOUTUBE_API_KEY']=str(st.secrets['YOUTUBE_API_KEY']).strip()
except Exception: pass
DEFAULT={'step':1,'country':'','themes':[],'theme_rank':[],'base':'','accent':[],'genre_rank':[],'keywords':[],'keyword':'','ideas':[],'idea':0,'titles':[],'title':'','lyrics':[],'style':'CINEMATIC','arts':[],'long_art':0,'short_art':0,'spectrum':'BALOK','hook':'','cta':'Subscribe untuk full song','render':None}
for k,v in DEFAULT.items(): st.session_state.setdefault(k,v)

def lang(): return COUNTRIES[st.session_state.country][2]
def region(): return COUNTRIES[st.session_state.country][0]
def clean(x,n=500): return re.sub(r'\s+',' ',str(x or '')).strip()[:n]
def slug(x): return re.sub(r'[^a-z0-9]+','_',x.lower()).strip('_')[:70] or 'song'
def fmt(x):
 try:x=float(x)
 except:x=0
 return f'{x/1e6:.1f}M' if x>=1e6 else f'{x/1e3:.1f}K' if x>=1e3 else f'{int(x):,}'
def research_call(q,max_per=8):
 if research is None: raise RuntimeError('research.py tidak bisa dimuat: '+RESEARCH_ERR)
 if not os.environ.get('YOUTUBE_API_KEY'): raise RuntimeError('YOUTUBE_API_KEY belum diisi di Streamlit Secrets.')
 return research.research(', '.join(q),country=region(),language=COUNTRIES[st.session_state.country][1],max_per_keyword=max_per)
def avg(v): return round(sum(float(x.get('score',0)) for x in v)/len(v),1) if v else 0

def scan_themes():
 out=[]
 for name,q in THEMES[lang()]:
  r=research_call(q,6); v=r.get('videos',[])
  out.append({'Theme':name,'Opportunity':avg(v),'Evidence':len(v),'Views Evidence':sum(int(x.get('views',0)) for x in v),'Views/Day':int(sum(float(x.get('vpd',0)) for x in v))})
 return sorted(out,key=lambda x:(x['Opportunity'],x['Views/Day']),reverse=True)
def scan_genres():
 out=[]
 for group,q in GQ.items():
  r=research_call(q,6); v=r.get('videos',[]); subs=[]
  for g in GENRES[group]:
   try:
    rr=research_call([g+' music'],5); vv=rr.get('videos',[]); subs.append((g,avg(vv),len(vv)))
   except: pass
  subs.sort(key=lambda x:x[1],reverse=True)
  out.append({'Group':group,'Opportunity':avg(v),'Evidence':len(v),'Views Evidence':sum(int(x.get('views',0)) for x in v),'Top Subgenre':subs[0][0] if subs else GENRES[group][0],'Subgenre Score':subs[0][1] if subs else 0})
 return sorted(out,key=lambda x:(x['Subgenre Score'],x['Opportunity']),reverse=True)
def scan_keywords():
 qs=[f"{' '.join(st.session_state.themes)} {st.session_state.base} music",f"{' '.join(st.session_state.themes)} {st.session_state.base}"]
 r=research_call(qs,12); vids=r.get('videos',[]); stop={'the','and','for','with','from','official','video','music','song','songs','live','full','new','lagu','musik','yang','dan','untuk','dengan','dari','ini','itu','2024','2025','2026'}; d=defaultdict(lambda:[0,0,0,0,[]])
 for v in vids:
  words=[w for w in re.findall(r'[\w-]+',v.get('title','').lower()) if len(w)>2 and w not in stop]; base=max(float(v.get('score',0)),1)
  for n in (1,2):
   for i in range(len(words)-n+1):
    k=' '.join(words[i:i+n]); z=d[k]; z[0]+=base; z[1]+=1; z[2]+=int(v.get('views',0)); z[3]+=float(v.get('vpd',0));
    if len(z[4])<2:z[4].append(v.get('title',''))
 rows=[{'Keyword':k,'Signal':round(z[0],1),'Evidence':z[1],'Avg Opportunity':round(z[0]/z[1],1),'Views Evidence':z[2],'Views/Day':int(z[3]),'Example':' | '.join(z[4])} for k,z in d.items() if z[1]>=2]
 return sorted(rows,key=lambda x:(x['Avg Opportunity'],x['Signal']),reverse=True)[:20]
def gemini_keys():
    keys=[]
    # Preferred: one TOML array, allowing any number of keys/projects.
    try:
        raw=st.secrets.get('GEMINI_API_KEYS',[])
        if isinstance(raw,str):
            keys += [x.strip() for x in re.split(r'[\n,;]+',raw) if x.strip()]
        else:
            keys += [str(x).strip() for x in raw if str(x).strip()]
    except Exception:
        pass
    # Also accept GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...
    for i in range(1,21):
        k=os.environ.get(f'GEMINI_API_KEY_{i}','')
        if not k:
            try: k=st.secrets.get(f'GEMINI_API_KEY_{i}','')
            except Exception: k=''
        if k and str(k).strip(): keys.append(str(k).strip())
    # Backward-compatible single key.
    k=os.environ.get('GEMINI_API_KEY','')
    if not k:
        try: k=st.secrets.get('GEMINI_API_KEY','')
        except Exception: k=''
    if k and str(k).strip(): keys.append(str(k).strip())
    return list(dict.fromkeys(keys))

def ai_text(prompt):
    # Gemini failover: key/project 1 fails -> automatically try the next key.
    # We keep the current healthy key at the front for subsequent calls.
    keys=gemini_keys()
    if keys:
        model=os.environ.get('GEMINI_MODEL','gemini-2.5-flash')
        try:
            idx=int(st.session_state.get('gemini_index',0)) % len(keys)
        except Exception:
            idx=0
        errors=[]
        for offset in range(len(keys)):
            j=(idx+offset)%len(keys); key=keys[j]
            url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}'
            body=json.dumps({'contents':[{'parts':[{'text':prompt}]}], 'generationConfig':{'temperature':0.8}}).encode()
            try:
                req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(req,timeout=45) as r:
                    data=json.loads(r.read().decode())
                text=data['candidates'][0]['content']['parts'][0]['text'].strip()
                st.session_state['gemini_index']=j
                st.session_state['gemini_last']='Gemini account '+str(j+1)+' OK'
                return text
            except Exception as e:
                errors.append(f'Gemini {j+1}: {type(e).__name__}')
        st.session_state['gemini_last']='Semua Gemini gagal — memakai fallback template'

    # Optional OpenAI fallback if configured.
    key=os.environ.get('OPENAI_API_KEY','')
    if not key:
        try: key=st.secrets.get('OPENAI_API_KEY','')
        except Exception: key=''
    if key:
        url=os.environ.get('OPENAI_BASE_URL','https://api.openai.com/v1/chat/completions')
        model=os.environ.get('OPENAI_MODEL','gpt-5-mini')
        body=json.dumps({'model':model,'messages':[{'role':'system','content':'You are a professional music content strategist. Follow the requested language and return concise production-ready text.'},{'role':'user','content':prompt}],'temperature':0.8}).encode()
        try:
            req=urllib.request.Request(url,data=body,headers={'Content-Type':'application/json','Authorization':'Bearer '+key})
            with urllib.request.urlopen(req,timeout=45) as r: return json.loads(r.read().decode())['choices'][0]['message']['content'].strip()
        except Exception: pass
    return ''

def ideas():
 k=st.session_state.keyword or 'the selected theme'
 ai=ai_text(f'''Create exactly 5 original YouTube music content ideas. Target country: {st.session_state.country}. Themes: {', '.join(st.session_state.themes)}. Base genre: {st.session_state.base}. Keyword/topic: {k}. Language: {lang()}. Each idea must be a specific story/angle, not a generic genre description. Number 1-5 only.''')
 if ai:
  vals=[re.sub(r'^\s*\d+[.)-]\s*','',x).strip() for x in ai.splitlines() if x.strip()]
  if len(vals)>=5: return vals[:5]
 if lang()=='English': return [f'A character reaches a breaking point over {k}, then makes one decisive choice.',f'Two people want the same future, but {k} slowly forces them apart.',f'Someone looks successful outside while secretly fighting {k} every night.',f'A normal day turns into a confrontation when {k} exposes what everyone hid.',f'After losing something because of {k}, the character finds one reason to keep moving.']
 return [f'Seseorang mencapai titik jenuh karena {k}, lalu mengambil satu keputusan besar.',f'Dua orang menginginkan masa depan yang sama, tetapi {k} perlahan memisahkan mereka.',f'Di luar terlihat baik-baik saja, tetapi diam-diam seseorang berjuang melawan {k}.',f'Hari biasa berubah menjadi konflik ketika {k} membuka sesuatu yang disembunyikan.',f'Setelah kehilangan banyak hal karena {k}, seseorang menemukan alasan untuk terus berjalan.']
def titles():
 k=st.session_state.keyword.title() or 'THE STORY'
 if lang()=='English': return [f'{k} — I Couldn’t Hide It Anymore',f'{k} — The Price of Staying',f'{k} — Nobody Saw This Coming',f'{k} — One More Night to Survive',f'{k} — I Finally Said No']
 return [f'{k} — Aku Tak Bisa Sembunyikan Lagi',f'{k} — Harga yang Harus Dibayar',f'{k} — Tak Ada yang Melihat Ini',f'{k} — Satu Malam Lagi',f'{k} — Akhirnya Aku Bilang Tidak']
def lyric(title,idea,v):
 if lang()=='English': return f'''[{v} — ORIGINAL SONG]\n\n[Intro / Hook]\n{title}\nI feel it coming, I can’t turn away.\n\n[Verse 1]\nThe room is quiet but my mind won’t sleep,\nI carry promises I couldn’t keep.\nEverybody sees the face I show,\nNobody knows how deep it goes.\n\n[Pre-Chorus]\nIf I run, the truth runs too,\nIf I stay, I have to choose.\n\n[Chorus]\nI won’t hide it anymore,\nI won’t break behind this door.\nWhatever comes, whatever it costs,\nI will face what I have lost.\n\n[Verse 2]\n{clean(idea,180)}\nEvery small wound became a scar,\nEvery silent night showed who we are.\n\n[Bridge]\nNo perfect ending, no easy road,\nI walk through fear and drop the load.\n\n[Final Chorus]\nI won’t hide it anymore,\nLouder than the voice before.\nWhatever comes, whatever it costs,\nI will rise from what I lost.\n\n[Outro]\nStill here. Still moving.\n'''
 return f'''[{v} — LAGU ORIGINAL]\n\n[Intro / Hook]\n{title}\nAku merasa semuanya datang, tak bisa lagi menghindar.\n\n[Verse 1]\nMalam sunyi tapi kepala tak diam,\nBeban lama masih ikut berjalan.\nSemua melihat wajah yang kutunjukkan,\nTak ada yang tahu perang di dalam.\n\n[Pre-Chorus]\nKalau lari, kenyataan mengejar,\nKalau bertahan, aku harus sadar.\n\n[Chorus]\nAku takkan sembunyi lagi,\nTakkan runtuh di balik sepi.\nApa pun datang, apa pun harganya,\nKu hadapi semua yang pernah hilang.\n\n[Verse 2]\n{clean(idea,180)}\nLuka kecil berubah jadi cerita,\nMalam panjang mengajar siapa kita.\n\n[Bridge]\nTak ada akhir yang selalu mudah,\nBeban berkurang saat kulepas.\n\n[Final Chorus]\nAku takkan sembunyi lagi,\nLebih keras dari suara sepi.\nApa pun datang, apa pun harganya,\nKu bangkit dari semua yang hilang.\n\n[Outro]\nMasih di sini. Masih berjalan.\n'''
def arts(style):
 story=clean(st.session_state.ideas[st.session_state.idea] if st.session_state.ideas else '',240); acc=', '.join(st.session_state.accent) or 'subtle Javanese/Nusantara 5–10%'
 common=f'''Title: "{st.session_state.title}"\nStory: {story}\n{ART[style]}\n{acc}. Keep the base genre identity in the visual mood. No baked logo, no watermark, no unnecessary text. Main subject stays center-safe for 16:9 and 9:16 crop.\n'''
 return [common+'CONCEPT A: tight character close-up; face, hands and one environmental clue tell the story.',common+'CONCEPT B: wide cinematic environment; character small against a location symbolizing the conflict.',common+'CONCEPT C: bold visual metaphor; one striking object dominates while the character reacts naturally.']
def suno(): return f'''{GENRES.get(st.session_state.base,['modern rock'])[0]}, original composition, {', '.join(st.session_state.accent) if st.session_state.accent else 'subtle Javanese/Nusantara accent 5–10%'}, target language {lang()}. Immediate audio hook within 5 seconds, no empty intro, memorable chorus, dynamic build, emotional bridge, biggest final chorus. Modern polished production, punchy drums, controlled bass, expressive vocal, cinematic depth. Base genre dominant. 3:10–3:40, original melody and arrangement.'''
def seo():
 return {'title':st.session_state.title,'description':f"{st.session_state.title} — 3D GOKIL\n\nOriginal music built from market research.\nTheme: {', '.join(st.session_state.themes)}\nGenre: {st.session_state.base}\nTopic: {st.session_state.keyword}\n\n{st.session_state.ideas[st.session_state.idea] if st.session_state.ideas else ''}\n\n3D GOKIL — original music and cinematic visual storytelling.",'tags':', '.join([st.session_state.keyword,st.session_state.base,'original music','3D GOKIL']),'hashtags':'#3DGOKIL #OriginalMusic #'+re.sub(r'[^A-Za-z0-9]','',st.session_state.base.title())}

def reset():
 for k,v in DEFAULT.items(): st.session_state[k]=v
 st.rerun()

st.title('🔥 3D GOKIL MUSIC FACTORY')
st.caption('MARKET SCAN → BLUEPRINT → MUSIC → ARTWORK → RENDER → SEO')
st.progress(st.session_state.step/6,text=f"STEP {st.session_state.step}/6")

if st.session_state.step==1:
 st.header('① 🌍 SCAN MARKET'); st.write('Mulai dari negara. Tidak ada DNA/CINTA/genre yang dipaksakan.')
 opts=list(COUNTRIES); c=st.selectbox('TARGET COUNTRY',opts,index=opts.index(st.session_state.country) if st.session_state.country in opts else None,placeholder='Pilih negara...')
 if c:
  st.session_state.country=c; st.info(f"Target **{c}** • Bahasa: **{lang()}**")
  if st.button('🔎 SCAN TEMA & PASAR',type='primary',use_container_width=True):
   try:
    with st.spinner('Menganalisis tema...'): st.session_state.theme_rank=scan_themes()
    st.session_state.step=2; st.rerun()
   except Exception as e: st.error(str(e))
else:
 if st.session_state.step==2:
  st.header('② 🧬 BUILD BLUEPRINT'); st.success('TARGET: '+st.session_state.country)
  if st.session_state.theme_rank:
   d=pd.DataFrame(st.session_state.theme_rank); d['Views Evidence']=d['Views Evidence'].map(fmt); d['Views/Day']=d['Views/Day'].map(fmt); st.dataframe(d,use_container_width=True,hide_index=True)
   st.caption('Opportunity = skor internal video evidence, bukan search volume resmi.')
  labels=[x[0] for x in THEMES[lang()]]; st.session_state.themes=st.multiselect('PILIH TEMA',labels,default=st.session_state.themes)
  gs=list(GENRES); st.session_state.base=st.selectbox('BASE GENRE',gs,index=gs.index(st.session_state.base) if st.session_state.base in gs else None,placeholder='Pilih base genre...')
  if st.session_state.base: st.session_state.accent=st.multiselect('ACCENT / FUSION',[x for x in gs if x!=st.session_state.base],default=[x for x in st.session_state.accent if x!=st.session_state.base]); st.caption('Nuansa Jawa/Nusantara otomatis 5–10%.')
  a,b=st.columns(2)
  if a.button('⬅️ GANTI NEGARA',use_container_width=True): reset()
  if b.button('🚀 LANJUT GENRE + KEYWORD',type='primary',use_container_width=True):
   if not st.session_state.themes or not st.session_state.base: st.warning('Pilih tema dan Base Genre.')
   else: st.session_state.step=3; st.rerun()
 elif st.session_state.step==3:
  st.header('③ 🎵 MUSIC CONTENT ENGINE'); st.caption(f"{st.session_state.country} → {', '.join(st.session_state.themes)} → {st.session_state.base}")
  if not st.session_state.genre_rank:
   if st.button('📊 ANALYZE GENRE + SUBGENRE',type='primary',use_container_width=True):
    try:
     with st.spinner('Membandingkan genre...'): st.session_state.genre_rank=scan_genres()
     st.rerun()
    except Exception as e: st.error(str(e))
  else:
   st.dataframe(pd.DataFrame(st.session_state.genre_rank),use_container_width=True,hide_index=True)
   if not st.session_state.keywords:
    if st.button('🔎 CARI KEYWORD / TOPIC',type='primary',use_container_width=True):
     try:
      with st.spinner('Mencari keyword dari video relevan...'): st.session_state.keywords=scan_keywords()
      st.rerun()
     except Exception as e: st.error(str(e))
   else:
    st.dataframe(pd.DataFrame(st.session_state.keywords),use_container_width=True,hide_index=True)
    choices=[x['Keyword'] for x in st.session_state.keywords[:12]]
    if choices: st.session_state.keyword=st.selectbox('PILIH KEYWORD / TOPIC',choices,index=choices.index(st.session_state.keyword) if st.session_state.keyword in choices else 0)
    if st.button('💡 GENERATE 5 CONTENT IDEAS',type='primary',use_container_width=True): st.session_state.ideas=ideas(); st.session_state.idea=0
    if st.session_state.ideas:
     st.subheader('💡 5 CONTENT IDEAS')
     for i,x in enumerate(st.session_state.ideas,1): st.markdown(f'**{i}.** {x}')
     st.session_state.idea=st.radio('PILIH SATU',range(5),index=st.session_state.idea,format_func=lambda x:f'Idea {x+1}',horizontal=True)
     if st.button('🎯 BUILD CLICK + SONG',type='primary',use_container_width=True):
      st.session_state.titles=titles(); st.session_state.title=st.session_state.titles[0]; st.session_state.lyrics=[lyric(st.session_state.title,st.session_state.ideas[st.session_state.idea],v) for v in ['EMOTIONAL','DARK','POWERFUL','SEMI-FUNNY','CINEMATIC']]; st.session_state.step=4; st.rerun()
  if st.button('⬅️ KEMBALI BLUEPRINT',use_container_width=True): st.session_state.step=2; st.rerun()
 elif st.session_state.step==4:
  st.header('④ 🎵 SONG + ARTWORK')
  st.session_state.title=st.radio('🎯 5 TITLE PILIHAN',st.session_state.titles,index=st.session_state.titles.index(st.session_state.title) if st.session_state.title in st.session_state.titles else 0)
  st.markdown('**RETENTION:** 0–5s hook → setup → build → chorus payoff → verse 2 → bridge → final chorus → short outro.')
  st.subheader('✍️ 5 LYRICS')
  for i,x in enumerate(st.session_state.lyrics,1):
   with st.expander(f'LYRICS {i}',expanded=i==1): st.text_area('Lyrics',x,height=330,key=f'lyr{i}')
  st.subheader('🎧 SUNO STYLE'); st.code(suno())
  st.subheader('🎨 ARTWORK'); styles=list(ART); st.session_state.style=st.selectbox('PILIH STYLE',styles,index=styles.index(st.session_state.style));
  if not st.session_state.arts or st.button('🎨 GENERATE 3 PROMPT',use_container_width=True): st.session_state.arts=arts(st.session_state.style)
  for i,p in enumerate(st.session_state.arts,1):
   with st.expander(f'CONCEPT {i}',expanded=i==1): st.text_area('Prompt',p,height=220,key=f'art{i}')
  if st.button('🎬 LANJUT RENDER',type='primary',use_container_width=True): st.session_state.step=5; st.rerun()
 elif st.session_state.step==5:
  st.header('⑤ 🎬 RENDER LONG + SHORT'); st.info('Render engine lama tetap dipakai. Factory ini menyiapkan paketnya.')
  names=[f'Concept {i+1}' for i in range(len(st.session_state.arts))]
  a,b=st.columns(2)
  st.session_state.long_art=a.selectbox('ARTWORK LONG',range(len(names)),index=st.session_state.long_art,format_func=lambda i:names[i]); st.session_state.short_art=b.selectbox('ARTWORK SHORT',range(len(names)),index=st.session_state.short_art,format_func=lambda i:names[i])
  st.session_state.spectrum=a.selectbox('SPECTRUM LONG',SPECTRUM,index=SPECTRUM.index(st.session_state.spectrum)); st.session_state.hook=b.text_input('HOOK 0–5s',value=st.session_state.hook or st.session_state.title); st.session_state.cta=b.selectbox('CTA',['Subscribe untuk full song','Follow untuk lagu berikutnya','Dengarkan versi LONG','Tanpa CTA'],index=['Subscribe untuk full song','Follow untuk lagu berikutnya','Dengarkan versi LONG','Tanpa CTA'].index(st.session_state.cta))
  st.code('3dgokil/\n├── short/\n│   ├── artwork/\n│   ├── music/\n│   ├── prompt/\n│   └── video/\n└── long/\n    ├── artwork/\n    ├── music/\n    ├── prompt/\n    └── video/',language='text')
  if st.button('🚀 BUAT RENDER PACKAGE',type='primary',use_container_width=True):
   st.session_state.render={'title':st.session_state.title,'country':st.session_state.country,'themes':st.session_state.themes,'genre':st.session_state.base,'accent':st.session_state.accent,'keyword':st.session_state.keyword,'idea':st.session_state.ideas[st.session_state.idea],'long':{'artwork':st.session_state.arts[st.session_state.long_art],'spectrum':st.session_state.spectrum,'logo':'FLOATING_SLOW','output':'long/video'},'short':{'artwork':st.session_state.arts[st.session_state.short_art],'hook':st.session_state.hook,'cta':st.session_state.cta,'spectrum':'NONE','logo':'STATIC','output':'short/video'},'suno':suno()}; st.success('Render package siap.')
  if st.session_state.render: st.download_button('⬇️ DOWNLOAD render_config.json',json.dumps(st.session_state.render,ensure_ascii=False,indent=2),file_name=f'{slug(st.session_state.title)}_render_config.json',mime='application/json',use_container_width=True)
  if st.button('➡️ LANJUT SEO',type='primary',use_container_width=True): st.session_state.step=6; st.rerun()
 elif st.session_state.step==6:
  st.header('⑥ 🚀 YOUTUBE SEO'); s=seo(); st.text_input('TITLE',s['title']); st.text_area('DESCRIPTION',s['description'],height=230); st.text_input('TAGS',s['tags']); st.text_input('HASHTAGS',s['hashtags'])
  project={'created_at':datetime.now().isoformat(),'brand':BRAND,'country':st.session_state.country,'themes':st.session_state.themes,'genre':st.session_state.base,'accent':st.session_state.accent,'keyword':st.session_state.keyword,'idea':st.session_state.ideas[st.session_state.idea],'title':st.session_state.title,'lyrics':st.session_state.lyrics,'artworks':st.session_state.arts,'suno':suno(),'render':st.session_state.render,'seo':s}
  st.download_button('⬇️ DOWNLOAD PROJECT JSON',json.dumps(project,ensure_ascii=False,indent=2),file_name=f'{slug(st.session_state.title)}_project.json',mime='application/json',use_container_width=True)
  st.success('🔥 PACKAGE LENGKAP — tinggal produksi/render dan upload ke channel baru.')
  if st.button('🔄 PROJECT BARU',type='primary',use_container_width=True): reset()
with st.sidebar:
 st.header('🔥 3D GOKIL'); st.write(f"STEP {st.session_state.step}/6"); st.caption('Workflow utama sengaja tidak ditaruh di sidebar agar HP simpel.'); st.caption('Research score = internal opportunity signal, bukan search volume resmi.')
 gk=gemini_keys()
 st.success(f'🤖 Gemini aktif: {len(gk)} key/project') if gk else st.warning('🤖 Gemini belum dipasang')
 if gk:
  st.caption(st.session_state.get('gemini_last','Failover otomatis aktif.'))
 st.divider()
 if st.button('↩️ RESET PROJECT'): reset()
