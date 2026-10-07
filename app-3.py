import streamlit as st
import re, json, os
from datetime import datetime

st.set_page_config(page_title='3D GOKIL AI Music Factory', page_icon='🔥', layout='wide')

BRAND='3D GOKIL'
MUSIC_DNAS={
'Indonesian Cyber-Mystic Rock Dangdut':dict(desc='Rock modern Indonesia + dangdut/koplo + cyber-mystic.',aud='Pendengar musik Indonesia yang suka rock, dangdut modern, satire, dan visual kuat.',emo='energik, misterius, relatable',topics=['realita kehidupan Indonesia','kerja','uang','keluarga','cinta','sosial','mistis'],style='modern Indonesian cyber-mystic rock dangdut, heavy guitars, energetic kendang, cinematic gamelan and bamboo flute, modern electronic texture',art='cinematic 3D Indonesian social realism, cyber-mystical atmosphere, neon green, deep crimson red, chrome highlights'),
'Music Sedih':dict(desc='Musik emosional tentang kehilangan, rindu, perjuangan, dan kesepian.',aud='Pendengar lagu galau, sedih, healing, rindu, kehilangan, dan lagu malam.',emo='sedih, hangat, rindu, reflektif',topics=['kehilangan','rindu','perpisahan','kesepian','keluarga','perjuangan','healing'],style='emotional Indonesian sad song, expressive male vocal, intimate piano, atmospheric electric guitar, warm bass, cinematic strings, gradual emotional build, memorable chorus',art='cinematic emotional 3D realism, lonely Indonesian character, rain, soft dramatic light, deep shadows, melancholic atmosphere'),
'Rock Marah':dict(desc='Rock keras dan rebel tentang tekanan hidup dan perlawanan.',aud='Pendengar rock/metal yang suka energi agresif dan kritik sosial.',emo='marah, rebel, berani, intens',topics=['tekanan hidup','ketidakadilan','kemunafikan','kerja','sistem','perlawanan'],style='aggressive modern Indonesian rock, distorted guitars, punchy drums, powerful male vocal, rebellious chorus, heavy bass, cinematic tension',art='cinematic gritty 3D realism, rebellious Indonesian character, industrial city, dramatic red lighting, smoke, chrome, high contrast'),
'Dangdut Koplo':dict(desc='Dangdut/koplo modern dengan groove kuat dan catchy.',aud='Pendengar dangdut Indonesia dan audience short-form yang suka lagu catchy.',emo='ceria, genit, galau, energik',topics=['cinta','jodoh','mantan','kehidupan','gaji','kerja','komedi'],style='modern Indonesian dangdut koplo, strong kendang groove, catchy vocal hook, melodic guitar, bass-driven rhythm, polished production, sing-along chorus',art='vibrant cinematic 3D Indonesian realism, expressive character, colorful night atmosphere, local details, humorous storytelling'),
'Mystical Music':dict(desc='Musik gelap, mistis, ritual, dan atmosferik dengan akar Indonesia.',aud='Pendengar musik mistis, folklore, urban legend, dan nuansa budaya Jawa/Indonesia.',emo='misterius, gelap, magis, tegang',topics=['mistis','ritual','folklore','malam','hutan','desa','urban legend'],style='dark Indonesian mystical music, low male vocal, deep drums, Javanese gamelan, bamboo flute, atmospheric drones, ritual percussion, haunting motifs',art='cinematic dark 3D realism, Indonesian mystical landscape, ancient temple, fog, moonlight, subtle supernatural elements'),
'Lo-fi Indonesia':dict(desc='Lo-fi Indonesia yang santai, hangat, dan cocok menemani aktivitas.',aud='Pendengar lo-fi, study/chill audience, pekerja, pelajar, dan penonton musik latar.',emo='tenang, nostalgia, hangat, sendu',topics=['malam','kopi','hujan','kota','belajar','kerja','nostalgia'],style='Indonesian lo-fi, warm mellow vocal, dusty drums, soft electric piano, subtle guitar, vinyl texture, relaxed bass, nostalgic atmosphere',art='cinematic cozy 3D realism, Indonesian room or city night, coffee, rain, warm lamp, nostalgic atmosphere')}

CATS={
'Indonesian Cyber-Mystic Rock Dangdut':['Gaji dan tanggal tua','Utang dan cicilan','Harga kebutuhan','Dunia kerja','Keluarga','Mantan','Kesepian','Teman palsu','Media sosial','Kecemasan'],
'Music Sedih':['Kehilangan','Rindu','Perpisahan','Mantan','Kesepian','Ayah','Ibu','Rumah','Lelah hidup','Healing'],
'Rock Marah':['Tekanan hidup','Ketidakadilan','Kemunafikan','Bos','Target','Lembur','Burnout','PHK','Gaji kecil','Tekanan sosial'],
'Dangdut Koplo':['Jodoh','Mantan','Cinta sederhana','Cemburu','Gebetan','Tetangga','Gaji','Kerja','Drama pasangan','Gagal move on'],
'Mystical Music':['Ritual malam','Pesugihan','Penunggu','Desa tua','Hutan','Rumah kosong','Jalan malam','Legenda lokal','Urban legend','Pantangan'],
'Lo-fi Indonesia':['Kopi malam','Hujan','Kamar kecil','Lampu kota','Belajar','Kerja malam','Menulis','Perjalanan','Masa sekolah','Nostalgia']}

SEEDS=[('MALAM YANG TIDAK SAMA','Seseorang menjalani malam biasa tetapi sebuah kejadian kecil membuat seluruh perasaannya berubah.'),('BESOK KITA COBA LAGI','Tokoh utama gagal hari ini tetapi memilih tidak berhenti.'),('YANG TIDAK PERNAH DIUCAPKAN','Perasaan yang terlalu lama disimpan akhirnya berubah menjadi lagu.'),('SATU HARI LAGI','Seseorang bertahan melewati hari berat sambil berharap keadaan membaik.'),('KITA PERNAH DI SINI','Sebuah tempat sederhana memunculkan kembali kenangan lama.'),('TIDAK SEMUA HARUS SEMPURNA','Tokoh utama belajar menerima hidup yang berantakan.'),('KETIKA KOTA MULAI TIDUR','Saat kota sepi, pikiran tokoh utama justru semakin ramai.'),('MASIH ADA JALAN','Saat semua pilihan tertutup, keputusan kecil membuka arah baru.'),('CERITA YANG BELUM SELESAI','Masalah lama kembali dan meminta sebuah keputusan.'),('HARI INI KITA BERTAHAN','Tokoh utama tidak memenangkan semua masalah, tetapi berhasil melewati hari itu.')]

def slug(s): return re.sub(r'[^a-z0-9]+','_',s.lower()).strip('_')
def dna(): return st.session_state.dna
def D(): return MUSIC_DNAS[dna()]
def stories(dna_name,sub):
 d=MUSIC_DNAS[dna_name]; out=[]
 for i,(a,b) in enumerate(SEEDS):
  hook=['Kalau kamu pernah merasakan ini, lagu ini untukmu.','Ada hal yang tidak bisa dijelaskan hanya dengan kata-kata.','Kita semua pernah berada di titik ini.','Hari ini berat. Tapi cerita ini belum selesai.','Dan malam ini semuanya terasa berbeda.'][i%5]
  out.append({'title':f'{a} — {sub}'.upper() if i<4 else f'{sub} — {a}'.upper(),'body':f'{b} Tema utama: {sub}. Konflik disampaikan sesuai DNA {dna_name}, dengan emosi {d["emo"]}.','hook':hook,'emotion':d['emo']})
 return out

def titles(story,dna_name,target,tone):
 t=story['title']; x=[t,f'{t} | {BRAND}',f'{t} | LAGU INDONESIA',f'DI BALIK {t}',f'MASIH ADA CERITA | {t}',f'{t} | FULL SONG']
 if dna_name=='Music Sedih' or tone=='Emotional': x+=['MASIH MENUNGGU','YANG TIDAK BISA KEMBALI','KITA PERNAH BERSAMA']
 elif dna_name=='Rock Marah' or tone=='Rebellious': x+=['KITA BUKAN MESIN','JANGAN SURUH KAMI DIAM','TIDAK AKAN TUNDUK']
 elif dna_name=='Dangdut Koplo': x+=['CINTA BEGINI AMAT','GAGAL MOVE ON LAGI','JODOH KE MANA?']
 elif dna_name=='Mystical Music': x+=['JANGAN DENGAR SENDIRIAN','RITUAL TENGAH MALAM','ADA YANG MEMANGGIL']
 elif dna_name=='Lo-fi Indonesia': x+=['MALAM, KOPI, DAN KENANGAN','HUJAN DI BALIK JENDELA','KOTA YANG TIDAK TIDUR']
 else: x+=['HIDUP SERIUS, TAPI GOKIL','GAJI MASUK, GAJI HILANG','REALITA TIDAK PUNYA MANUAL']
 return list(dict.fromkeys(x))[:15]

def score(t):
 w=re.findall(r'[A-Za-z0-9]+',t); return min(50,(15 if 2<=len(w)<=8 else 10)+(15 if len(t)<=48 else 9)+(10 if t.isupper() else 7)+10)

def suno(dna_name):
 d=MUSIC_DNAS[dna_name]; return f'''{d["style"]}. Emotion: {d["emo"]}. Audience: {d["aud"]}. Strong recognizable musical identity, memorable chorus, quick hook, polished production, clear vocal, controlled low end, no unnecessarily long intro.'''

def lyrics(title,s,dna_name):
 return f'''[INTRO — 0:00–0:08]\n[Audio hook langsung]\n{s["hook"]}\n\n[VERSE 1]\n{s["body"]}\nKita berjalan melewati malam\nMembawa cerita yang belum padam\n\n[PRE-CHORUS]\nKalau hari ini terasa berat\nTarik napas, jangan menyerah\n\n[CHORUS — MAIN HOOK]\n{title.upper()}\nKita masih di sini\n{s["hook"]}\nDan cerita belum berhenti\n\n[VERSE 2]\nAda hari ketika langkah melambat\nAda malam ketika hati penat\nTapi selama masih ada suara\nKita nyanyikan semua cerita\n\n[BRIDGE]\n[Build sesuai DNA: {dna_name}]\nYang hilang biarkan menjadi kenangan\nYang tersisa kita jadikan alasan\nUntuk terus berjalan\n\n[FINAL CHORUS]\n{title.upper()}\nKita masih di sini\nDan cerita belum berhenti\n\n[OUTRO]\n[Motif khas DNA — ending mudah di-loop]'''

def art(dna_name,title,s,ratio,variant='Cinematic'):
 d=MUSIC_DNAS[dna_name]
 extra={'Cinematic':'strong cinematic realism and dimensional depth','GOKIL / Absurd':'one clever absurd visual detail without becoming cartoonish','Dark / Mystical':'darker mystery, fog, dramatic shadows and subtle supernatural tension','Social / Relatable':'highly relatable everyday Indonesian situation and expressive character acting','Stop-scroll':'instantly readable central composition, strong silhouette and one visual surprise'}[variant]
 return f'''Create a {ratio} cinematic 3D music artwork for 3D GOKIL. MUSIC DNA: {dna_name}. TITLE: {title}. STORY: {s["body"]}. Visual DNA: {d["art"]}. Emotion: {d["emo"]}. {extra}. Highly dimensional, realistic, memorable focal subject. LONG: keep lower 18–22% relatively clean for future spectrum. SHORT: prioritize mobile readability. Do NOT render 3D GOKIL, title text, spectrum, equalizer, watermark, or random text into the image.'''

def seo(dna_name,title,s,target):
 d=MUSIC_DNAS[dna_name]; kws=[title,dna_name,'musik Indonesia','lagu Indonesia','3D GOKIL']+d['topics'][:5]
 desc=f'{title} — 3D GOKIL\n\nMusic DNA: {dna_name}\n\n{s["body"]}\n\n{d["desc"]}\n\nTarget: {target}\n\n#3DGOKIL #MusikIndonesia'
 return desc,', '.join(dict.fromkeys(kws))

for k,v in {'dna':list(MUSIC_DNAS)[0],'stories':[],'story_i':0,'titles':[],'final_title':'','lyrics':'','research':{}}.items(): st.session_state.setdefault(k,v)

with st.sidebar:
 st.header('🧬 MUSIC DNA')
 new=st.selectbox('Pilih DNA Musik',list(MUSIC_DNAS),index=list(MUSIC_DNAS).index(st.session_state.dna))
 if new!=st.session_state.dna:
  st.session_state.dna=new; st.session_state.stories=[]; st.session_state.titles=[]; st.session_state.final_title=''; st.session_state.lyrics=''
 st.success(new); st.caption(D()['desc'])
 target=st.selectbox('🎯 Target Audience',['Indonesia','Indonesia + Global','Global'])
 tone=st.selectbox('🎭 Tone',['Auto','Emotional','Energetic','Rebellious','Dark','Chill'])
 st.divider(); st.write('**SHORT:** discovery / subscriber'); st.write('**LONG:** full song / watch time')

st.title('🔥 3D GOKIL AI MUSIC FACTORY')
st.caption('Brand tetap 3D GOKIL • Music DNA bisa berubah • Research → Story → Title → Lyric → Suno → Artwork → SEO → Export')

with st.expander('🧬 DNA DASHBOARD',True):
 c1,c2,c3,c4=st.columns(4); c1.metric('Music DNA',dna()); c2.metric('Emotion',D()['emo']); c3.metric('Target',target); c4.metric('Output','SHORT + LONG')
 st.write('**Audience:**',D()['aud']); st.write('**Core topics:**',' • '.join(D()['topics']))

tabs=st.tabs(['🔎 RESEARCH','🎭 STORY','🎯 TITLE','✍️ LYRIC','🎸 SUNO','🖼️ ARTWORK','🚀 SEO','📦 EXPORT'])

with tabs[0]:
 st.header('🔎 Audience & Trend Research')
 keyword=st.text_input('Keyword / topik riset',D()['topics'][0]); country=st.selectbox('Negara target',['Indonesia','United States','Malaysia','Singapore','Worldwide']); language=st.selectbox('Bahasa',['Indonesian','English','Malay'])
 api=bool(os.getenv('YOUTUBE_API_KEY')); st.metric('YouTube API','READY' if api else 'BELUM TERHUBUNG')
 if st.button('🔎 ANALISIS PELUANG',use_container_width=True):
  st.session_state.research={'keyword':keyword,'country':country,'language':language,'dna':dna(),'time':datetime.now().isoformat(timespec='seconds')}
 if st.session_state.research:
  st.success(f'Profile: {keyword} • {country} • {language} • DNA: {dna()}')
  st.info('Layer ini menjaga riset mengikuti DNA aktif. Data live YouTube harus dipanggil dari research.py/API; app tidak mengarang angka jika API belum dipakai.')

with tabs[1]:
 st.header('🎭 Story / Theme Lab'); cats=CATS[dna()]; cat=st.selectbox('Kategori',list(cats)); sub=st.selectbox('Sub-theme',cats[cat]); custom=st.text_input('Sub-theme custom'); sub=custom.strip() or sub
 if st.button('🔥 GENERATE 10 STORY',use_container_width=True): st.session_state.stories=stories(dna(),sub); st.session_state.story_i=0; st.session_state.titles=[]; st.session_state.final_title=''; st.session_state.lyrics=''
 for i,s in enumerate(st.session_state.stories):
  with st.container(border=True):
   st.markdown(f'### {i+1:02d}. {s["title"]}'); st.write(s['body']); st.caption(f'🎭 {s["emotion"]} | 🎣 {s["hook"]}')
   if st.button(f'👉 PILIH STORY {i+1:02d}',key=f's{i}'): st.session_state.story_i=i; st.session_state.titles=[]; st.session_state.final_title=''; st.session_state.lyrics=''
 if st.session_state.stories: st.success('Story aktif: '+st.session_state.stories[st.session_state.story_i]['title'])

with tabs[2]:
 st.header('🎯 Title Lab')
 if st.session_state.stories:
  s=st.session_state.stories[st.session_state.story_i]
  if st.button('🚀 GENERATE TITLE OPTIONS',use_container_width=True): st.session_state.titles=titles(s,dna(),target,tone)
  for i,t in enumerate(sorted(st.session_state.titles,key=score,reverse=True)):
   a,b=st.columns([6,1]); a.write(f'**{i+1}. {t}**'); b.write(f'{score(t)}/50')
   if st.button(f'USE #{i+1}',key=f't{i}'): st.session_state.final_title=t
  if st.session_state.final_title: st.success('🔥 '+st.session_state.final_title)
 else: st.info('Pilih story terlebih dahulu.')

with tabs[3]:
 st.header('✍️ Lyric Lab')
 if st.session_state.stories:
  s=st.session_state.stories[st.session_state.story_i]; title=st.text_input('Judul lagu',st.session_state.final_title or s['title'])
  if st.button('🎤 GENERATE LYRICS',use_container_width=True): st.session_state.lyrics=lyrics(title,s,dna())
 st.session_state.lyrics=st.text_area('Lyrics — editable',st.session_state.lyrics,height=520)

with tabs[4]:
 st.header('🎸 Suno Style — DNA Aktif'); st.code(suno(dna()),language='text'); st.download_button('⬇️ DOWNLOAD SUNO STYLE',suno(dna()),f'{slug(dna())}_suno.txt','text/plain')

with tabs[5]:
 st.header('🖼️ Artwork Lab — 5 konsep'); s=st.session_state.stories[st.session_state.story_i] if st.session_state.stories else {'title':'JUDUL LAGU','body':D()['desc'],'hook':''}; title=st.session_state.final_title or s['title']
 for v in ['Cinematic','GOKIL / Absurd','Dark / Mystical','Social / Relatable','Stop-scroll']:
  st.markdown(f'### {v}'); st.code(art(dna(),title,s,'16:9',v)); st.code(art(dna(),title,s,'9:16',v))

with tabs[6]:
 st.header('🚀 YouTube SEO'); s=st.session_state.stories[st.session_state.story_i] if st.session_state.stories else {'title':'JUDUL LAGU','body':D()['desc']}; title=st.session_state.final_title or s['title']; desc,kws=seo(dna(),title,s,target)
 st.text_input('YouTube Title',title); st.text_area('Description',desc,height=280); st.text_input('Keywords',kws); st.text_input('Hashtags',f'#3DGOKIL #{slug(dna()).replace("_","")} #MusikIndonesia')

with tabs[7]:
 st.header('📦 Export Project Metadata'); s=st.session_state.stories[st.session_state.story_i] if st.session_state.stories else {'title':'JUDUL LAGU','body':D()['desc'],'hook':''}; title=st.session_state.final_title or s['title']
 meta={'brand':BRAND,'music_dna':dna(),'target':target,'tone':tone,'story':s,'title':title,'lyrics':st.session_state.lyrics,'suno_style':suno(dna()),'artwork_long_prompt':art(dna(),title,s,'16:9'),'artwork_short_prompt':art(dna(),title,s,'9:16'),'created_at':datetime.now().isoformat(),'strategy':{'long':'full song / watch time','short':'discovery / subscriber'}}
 st.json(meta); st.download_button('⬇️ DOWNLOAD PROJECT JSON',json.dumps(meta,ensure_ascii=False,indent=2),f'{slug(title)}_project.json','application/json',use_container_width=True)

st.divider(); st.caption('🔥 3D GOKIL AI MUSIC FACTORY • Brand tetap • Music DNA fleksibel')
