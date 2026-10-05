import streamlit as st, json, re
st.set_page_config(page_title="3D GOKIL AI MUSIC FACTORY", page_icon="🎧", layout="wide")
st.markdown("""<style>
.stApp{background:#08090d;color:#f5f5f5}
div.stButton>button{border:1px solid #39FF14;border-radius:12px;font-weight:700}
.gbox{border:1px solid #39FF14;border-radius:15px;padding:15px;background:#11131a}
</style>""",unsafe_allow_html=True)
st.title("🎸 3D GOKIL")
st.header("AI MUSIC FACTORY — V1")
st.markdown('<div class="gbox"><b>DNA:</b> <span style="color:#39FF14">NEON GREEN</span> + <span style="color:#FF1744">CRIMSON RED</span><br>Indonesian Cyber-Mystic Rock Dangdut</div>',unsafe_allow_html=True)
st.caption("V1 tanpa API berbayar: draft dan prompt lokal yang bisa diedit. Integrasi AI, gambar, audio, FFmpeg dan YouTube menyusul.")
with st.sidebar:
    st.subheader("⚙️ DNA 3D GOKIL")
    dna=st.selectbox("Identitas musik",["Indonesian Cyber-Mystic Rock Dangdut","Industrial Rock Dangdut","Heavy Rock Indonesia","Modern Dangdut Rock"])
    palette=st.text_input("Palet visual","black, neon green, deep crimson red, chrome highlights")
st.subheader("🎯 Konsep Lagu")
a,b=st.columns(2)
with a:
    title=st.text_input("Judul lagu","GAJI MASUK, GAJI HILANG")
    theme=st.text_input("Tema / cerita","gaji habis untuk kebutuhan hidup, tetapi tetap berjuang")
    genre=st.selectbox("Genre",["Modern Rock Dangdut","Heavy Rock","Industrial Metal","Dangdut Modern","Alternative Rock"])
    mood=st.selectbox("Mood",["Marah tapi membangkitkan semangat","Gelap dan mistis","Sedih tapi kuat","Satir dan jenaka","Romantis"])
with b:
    vocal=st.selectbox("Vokal",["Male vocal","Female vocal","Duet"])
    duration=st.selectbox("Durasi",["3:00–3:20","3:20–3:40","3:40–4:00"])
    energy=st.slider("Energi",1,100,90)
    hook=st.text_input("Hook utama","GAJI MASUK, GAJI HILANG! BELUM SEMPAT PEGANG SUDAH TERBANG!")
def slug(s): return re.sub(r"[^a-z0-9]+","_",s.lower()).strip("_")
def build():
    h=hook.strip() or title.upper()+"!"
    lyrics=f"""[Intro — langsung riff gitar kuat, kendang rapat, aksen gamelan]
{h}
{h}

[Verse 1 — groove rock dangdut]
{theme.capitalize()}
Hari berjalan, beban berdatangan
Kita bertahan di tengah keadaan
Banyak yang bicara, sedikit memahami
Namun langkah ini tak berhenti

[Pre-Chorus — build up]
Tarik napas, kepalkan tangan
Jangan biarkan harapan menghilang

[Chorus — besar dan mudah diingat]
{h}
Kita masih berdiri, belum menyerah
Walau dunia terasa makin susah
Suara kita tak akan kalah!

[Verse 2]
Lampu kota menjadi saksi
Tentang mimpi yang belum terganti
Jatuh sekali, bangkit kembali
Kita hadapi hari demi hari

[Bridge — emosional]
Kalau malam terasa panjang
Jangan percaya kita sendirian
Selama jantung masih berdetak
Masih ada alasan untuk bergerak

[Breakdown — gitar berat + kendang]
HEY! BANGKIT! HEY! BERDIRI!
KITA BELUM SELESAI!

[Final Chorus — paling megah]
{h}
Kita masih berdiri, belum menyerah
Walau dunia terasa makin susah
KITA BELUM KALAH!

[Outro — hentakan terakhir]
Kita belum kalah..."""
    style=f"{dna}, {genre}, {vocal}, {mood.lower()}, energetic emotional performance, memorable vocal hook within first 5–8 seconds, powerful sing-along chorus, tight distorted electric guitar riffs, punchy bass, energetic Indonesian dangdut kendang groove, subtle electronic production, tasteful Javanese gamelan accents, dynamic breakdown, explosive final chorus, clean modern mix, target duration {duration}, energy {energy}/100."
    avoid="No long intro, no excessive instrumental solo, no muddy bass, no overcrowded arrangement, no extreme screaming, no weak chorus, no abrupt unfinished ending."
    base=f"""Cinematic high-detail 3D music artwork for 3D GOKIL. Theme: {theme}. Mood: {mood}. Indonesian setting and believable cultural details. Visual identity: {palette}. Dramatic cinematic lighting, strong focal subject, rich depth, professional album-cover composition. Title "{title.upper()}" top-left in bold distressed chrome-metal lettering. Small 3D GOKIL branding. No extra text, no watermark, no misspelled lettering."""
    desc=f"""{title} — karya musik original dari 3D GOKIL.
Tema: {theme}
Genre: {genre} | Identitas: {dna}

Dengarkan sampai akhir dan tulis bagian favoritmu di komentar. Jangan lupa LIKE, KOMENTAR, dan SUBSCRIBE untuk rilisan berikutnya."""
    return {"title":title,"theme":theme,"genre":genre,"mood":mood,"lyrics":lyrics,"suno_style":style,"avoid":avoid,"art_long":base+"\nLandscape 16:9 YouTube full-song artwork.","art_short":base+"\nVertical 9:16 mobile composition; recompose subject and title safely inside frame.","youtube_title":f"{title} | 3D GOKIL | {genre}","description":desc,"hashtags":f"#3DGOKIL #{slug(title).replace('_','')} #MusikIndonesia #IndonesianRock #RockDangdut","tags":", ".join([title,"3D GOKIL",genre,"musik Indonesia","rock dangdut","Indonesian rock","original music"])}
if st.button("🔥 BUAT PAKET PRODUKSI",type="primary",use_container_width=True):
    st.session_state.pkg=build()
if "pkg" in st.session_state:
    p=st.session_state.pkg
    st.divider(); st.subheader("📦 Paket Produksi — edit sebelum digunakan")
    tabs=st.tabs(["✍️ Lirik","🎸 Suno Style","🖼️ Artwork","🚀 YouTube SEO"])
    with tabs[0]: p["lyrics"]=st.text_area("Lirik",p["lyrics"],height=420)
    with tabs[1]:
        p["suno_style"]=st.text_area("Style Suno",p["suno_style"],height=180)
        p["avoid"]=st.text_area("Avoid / Negative",p["avoid"],height=100)
    with tabs[2]:
        p["art_long"]=st.text_area("Artwork LONG — 16:9",p["art_long"],height=200)
        p["art_short"]=st.text_area("Artwork SHORT — 9:16",p["art_short"],height=200)
    with tabs[3]:
        p["youtube_title"]=st.text_input("YouTube title",p["youtube_title"])
        p["description"]=st.text_area("Description",p["description"],height=150)
        p["hashtags"]=st.text_input("Hashtags",p["hashtags"])
        p["tags"]=st.text_area("Tags / keywords",p["tags"],height=80)
    st.session_state.pkg=p
    st.download_button("⬇️ EXPORT PROJECT JSON",json.dumps(p,ensure_ascii=False,indent=2),file_name=slug(title)+"_3dgokil.json",mime="application/json",use_container_width=True)
    st.info("SEO membantu relevansi metadata, bukan jaminan video direkomendasikan YouTube.")
else: st.info("Isi konsep lagu, lalu tekan BUAT PAKET PRODUKSI.")
st.caption("V1 • Draft lokal tanpa API. Output perlu diperiksa dan diedit. Render video dan AI generation penuh masuk V2.")
