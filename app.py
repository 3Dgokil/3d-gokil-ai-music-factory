import os
import re
import json
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="3D GOKIL AI Music Factory", page_icon="🔥", layout="wide")

BRAND = "3D GOKIL"

MUSIC_DNAS = {
    "Indonesian Cyber-Mystic Rock Dangdut": {
        "desc": "Rock modern Indonesia + dangdut/koplo + cyber-mystic.",
        "aud": "Pendengar musik Indonesia yang suka rock, dangdut modern, satire, dan visual kuat.",
        "emo": "energik, misterius, relatable",
        "topics": ["realita kehidupan Indonesia", "kerja", "uang", "keluarga", "cinta", "sosial", "mistis"],
        "style": "Modern Indonesian Cyber-Mystic Rock Dangdut, heavy rock guitars, energetic kendang groove, cinematic gamelan and bamboo flute accents, modern electronic texture",
        "art": "cinematic 3D Indonesian social realism, cyber-mystical atmosphere, neon green, deep crimson red, chrome highlights",
    },
    "Music Sedih": {
        "desc": "Musik emosional tentang kehilangan, rindu, perjuangan, dan kesepian.",
        "aud": "Pendengar lagu galau, sedih, healing, rindu, kehilangan, dan lagu malam.",
        "emo": "sedih, hangat, rindu, reflektif",
        "topics": ["kehilangan", "rindu", "perpisahan", "kesepian", "keluarga", "perjuangan", "healing"],
        "style": "Emotional Indonesian sad song, expressive male vocal, intimate piano, atmospheric electric guitar, warm bass, cinematic strings, gradual emotional build, memorable chorus",
        "art": "cinematic emotional 3D realism, lonely Indonesian character, rain, soft dramatic light, deep shadows, melancholic atmosphere",
    },
    "Rock Marah": {
        "desc": "Rock keras dan rebel tentang tekanan hidup dan perlawanan.",
        "aud": "Pendengar rock/metal yang suka energi agresif dan kritik sosial.",
        "emo": "marah, rebel, berani, intens",
        "topics": ["tekanan hidup", "ketidakadilan", "kemunafikan", "kerja", "sistem", "perlawanan"],
        "style": "Aggressive modern Indonesian rock, distorted guitars, punchy drums, powerful male vocal, rebellious chorus, heavy bass, cinematic tension",
        "art": "cinematic gritty 3D realism, rebellious Indonesian character, industrial city, dramatic red lighting, smoke, chrome, high contrast",
    },
    "Dangdut Koplo": {
        "desc": "Dangdut/koplo modern dengan groove kuat dan catchy.",
        "aud": "Pendengar dangdut Indonesia dan audience short-form yang suka lagu catchy.",
        "emo": "ceria, genit, galau, energik",
        "topics": ["cinta", "jodoh", "mantan", "kehidupan", "gaji", "kerja", "komedi"],
        "style": "Modern Indonesian dangdut koplo, strong kendang groove, catchy vocal hook, melodic guitar, bass-driven rhythm, polished production, sing-along chorus",
        "art": "vibrant cinematic 3D Indonesian realism, expressive character, colorful night atmosphere, local details, humorous storytelling",
    },
    "Mystical Music": {
        "desc": "Musik gelap, mistis, ritual, dan atmosferik dengan akar Indonesia.",
        "aud": "Pendengar musik mistis, folklore, urban legend, dan nuansa budaya Jawa/Indonesia.",
        "emo": "misterius, gelap, magis, tegang",
        "topics": ["mistis", "ritual", "folklore", "malam", "hutan", "desa", "urban legend"],
        "style": "Dark Indonesian mystical music, low male vocal, deep drums, Javanese gamelan, bamboo flute, atmospheric drones, ritual percussion, haunting motifs",
        "art": "cinematic dark 3D realism, Indonesian mystical landscape, ancient temple, fog, moonlight, subtle supernatural elements",
    },
    "Lo-fi Indonesia": {
        "desc": "Lo-fi Indonesia yang santai, hangat, dan cocok menemani aktivitas.",
        "aud": "Pendengar lo-fi, study/chill audience, pekerja, pelajar, dan penonton musik latar.",
        "emo": "tenang, nostalgia, hangat, sendu",
        "topics": ["malam", "kopi", "hujan", "kota", "belajar", "kerja", "nostalgia"],
        "style": "Indonesian lo-fi, warm mellow vocal, dusty drums, soft electric piano, subtle guitar, vinyl texture, relaxed bass, nostalgic atmosphere",
        "art": "cinematic cozy 3D realism, Indonesian room or city night, coffee, rain, warm lamp, nostalgic atmosphere",
    },
}

CATS = {
    "Indonesian Cyber-Mystic Rock Dangdut": ["Gaji dan tanggal tua", "Utang dan cicilan", "Harga kebutuhan", "Dunia kerja", "Keluarga", "Mantan", "Kesepian", "Teman palsu", "Media sosial", "Kecemasan"],
    "Music Sedih": ["Kehilangan", "Rindu", "Perpisahan", "Mantan", "Kesepian", "Ayah", "Ibu", "Rumah", "Lelah hidup", "Healing"],
    "Rock Marah": ["Tekanan hidup", "Ketidakadilan", "Kemunafikan", "Bos", "Target", "Lembur", "Burnout", "PHK", "Gaji kecil", "Tekanan sosial"],
    "Dangdut Koplo": ["Jodoh", "Mantan", "Cinta sederhana", "Cemburu", "Gebetan", "Tetangga", "Gaji", "Kerja", "Drama pasangan", "Gagal move on"],
    "Mystical Music": ["Ritual malam", "Pesugihan", "Penunggu", "Desa tua", "Hutan", "Rumah kosong", "Jalan malam", "Legenda lokal", "Urban legend", "Pantangan"],
    "Lo-fi Indonesia": ["Kopi malam", "Hujan", "Kamar kecil", "Lampu kota", "Belajar", "Kerja malam", "Menulis", "Perjalanan", "Masa sekolah", "Nostalgia"],
}

SEEDS = [
    ("MALAM YANG TIDAK SAMA", "Seseorang menjalani malam biasa tetapi sebuah kejadian kecil membuat seluruh perasaannya berubah."),
    ("BESOK KITA COBA LAGI", "Tokoh utama gagal hari ini tetapi memilih tidak berhenti."),
    ("YANG TIDAK PERNAH DIUCAPKAN", "Perasaan yang terlalu lama disimpan akhirnya berubah menjadi lagu."),
    ("SATU HARI LAGI", "Seseorang bertahan melewati hari berat sambil berharap keadaan membaik."),
    ("KITA PERNAH DI SINI", "Sebuah tempat sederhana memunculkan kembali kenangan lama."),
    ("TIDAK SEMUA HARUS SEMPURNA", "Tokoh utama belajar menerima hidup yang berantakan."),
    ("KETIKA KOTA MULAI TIDUR", "Saat kota sepi, pikiran tokoh utama justru semakin ramai."),
    ("MASIH ADA JALAN", "Saat semua pilihan tertutup, keputusan kecil membuka arah baru."),
    ("CERITA YANG BELUM SELESAI", "Masalah lama kembali dan meminta sebuah keputusan."),
    ("HARI INI KITA BERTAHAN", "Tokoh utama tidak memenangkan semua masalah, tetapi berhasil melewati hari itu."),
]

PAGES = ["🔎 RESEARCH", "🎭 STORY", "🎯 TITLE", "✍️ LYRIC", "🎸 SUNO", "🖼️ ARTWORK", "🚀 SEO", "📦 EXPORT"]

for key, default in {
    "dna": list(MUSIC_DNAS)[0],
    "target": "Indonesia",
    "tone": "Auto",
    "page": PAGES[0],
    "stories": [],
    "story_i": 0,
    "titles": [],
    "final_title": "",
    "lyrics": "",
    "research_results": [],
    "research_meta": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Repair stale session values safely after an app update.
if st.session_state.get("dna") not in MUSIC_DNAS:
    st.session_state.dna = list(MUSIC_DNAS)[0]
if st.session_state.get("target") not in ["Indonesia", "Indonesia + Global", "Global"]:
    st.session_state.target = "Indonesia"
if st.session_state.get("tone") not in ["Auto", "Emotional", "Energetic", "Rebellious", "Dark", "Chill"]:
    st.session_state.tone = "Auto"
if st.session_state.get("page") not in PAGES:
    st.session_state.page = PAGES[0]


def D():
    return MUSIC_DNAS.get(st.session_state.get("dna"), MUSIC_DNAS[list(MUSIC_DNAS)[0]])


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", str(text).lower()).strip("_") or "3d_gokil"


def build_stories(dna_name, sub):
    d = MUSIC_DNAS[dna_name]
    hooks = [
        "Kalau kamu pernah merasakan ini, lagu ini untukmu.",
        "Ada hal yang tidak bisa dijelaskan hanya dengan kata-kata.",
        "Kita semua pernah berada di titik ini.",
        "Hari ini berat. Tapi cerita ini belum selesai.",
        "Dan malam ini semuanya terasa berbeda.",
    ]
    out = []
    for i, (a, b) in enumerate(SEEDS):
        title = f"{a} — {sub}" if i < 4 else f"{sub} — {a}"
        out.append({
            "title": title.upper(),
            "body": f"{b} Tema utama: {sub}. Konflik disampaikan sesuai DNA {dna_name}, dengan emosi {d['emo']}.",
            "hook": hooks[i % len(hooks)],
            "emotion": d["emo"],
        })
    return out


def make_titles(story, dna_name, target, tone):
    t = story["title"]
    x = [
        t, f"{t} | {BRAND}", f"{t} | LAGU INDONESIA", f"DI BALIK {t}",
        f"MASIH ADA CERITA | {t}", f"{t} | FULL SONG",
    ]
    if dna_name == "Music Sedih" or tone == "Emotional":
        x += ["MASIH MENUNGGU", "YANG TIDAK BISA KEMBALI", "KITA PERNAH BERSAMA"]
    elif dna_name == "Rock Marah" or tone == "Rebellious":
        x += ["KITA BUKAN MESIN", "JANGAN SURUH KAMI DIAM", "TIDAK AKAN TUNDUK"]
    elif dna_name == "Dangdut Koplo":
        x += ["CINTA BEGINI AMAT", "GAGAL MOVE ON LAGI", "JODOH KE MANA?"]
    elif dna_name == "Mystical Music":
        x += ["JANGAN DENGAR SENDIRIAN", "RITUAL TENGAH MALAM", "ADA YANG MEMANGGIL"]
    elif dna_name == "Lo-fi Indonesia":
        x += ["MALAM, KOPI, DAN KENANGAN", "HUJAN DI BALIK JENDELA", "KOTA YANG TIDAK TIDUR"]
    else:
        x += ["HIDUP SERIUS, TAPI GOKIL", "GAJI MASUK, GAJI HILANG", "REALITA TIDAK PUNYA MANUAL"]
    if target != "Indonesia":
        x += [f"{t} | INDONESIAN MUSIC", f"{t} | INDONESIAN SONG"]
    return list(dict.fromkeys(x))[:15]


def score_title(t):
    words = re.findall(r"[A-Za-z0-9]+", t)
    return min(50, (15 if 2 <= len(words) <= 8 else 10) + (15 if len(t) <= 48 else 9) + (10 if t.isupper() else 7) + 10)


def suno(dna_name):
    d = MUSIC_DNAS[dna_name]
    return f"{d['style']}. Emotion: {d['emo']}. Audience: {d['aud']}. Strong recognizable musical identity, memorable chorus, quick hook, polished production, clear vocal, controlled low end, no unnecessarily long intro."


def make_lyrics(title, story, dna_name):
    return f"""[INTRO — 0:00–0:08]\n[Audio hook langsung]\n{story['hook']}\n\n[VERSE 1]\n{story['body']}\nKita berjalan melewati malam\nMembawa cerita yang belum padam\n\n[PRE-CHORUS]\nKalau hari ini terasa berat\nTarik napas, jangan menyerah\n\n[CHORUS — MAIN HOOK]\n{title.upper()}\nKita masih di sini\n{story['hook']}\nDan cerita belum berhenti\n\n[VERSE 2]\nAda hari ketika langkah melambat\nAda malam ketika hati penat\nTapi selama masih ada suara\nKita nyanyikan semua cerita\n\n[BRIDGE]\n[Build sesuai DNA: {dna_name}]\nYang hilang biarkan menjadi kenangan\nYang tersisa kita jadikan alasan\nUntuk terus berjalan\n\n[FINAL CHORUS]\n{title.upper()}\nKita masih di sini\nDan cerita belum berhenti\n\n[OUTRO]\n[Motif khas DNA — ending mudah di-loop]"""


def artwork(dna_name, title, story, ratio, variant):
    d = MUSIC_DNAS[dna_name]
    extras = {
        "Cinematic": "strong cinematic realism and dimensional depth",
        "GOKIL / Absurd": "one clever absurd visual detail without becoming cartoonish",
        "Dark / Mystical": "darker mystery, fog, dramatic shadows and subtle supernatural tension",
        "Social / Relatable": "highly relatable everyday Indonesian situation and expressive character acting",
        "Stop-scroll": "instantly readable central composition, strong silhouette and one visual surprise",
    }
    return f"""Create a {ratio} cinematic 3D music artwork for 3D GOKIL.\nMUSIC DNA: {dna_name}\nTITLE CONCEPT: {title}\nSTORY: {story['body']}\nVisual DNA: {d['art']}\nEmotion: {d['emo']}\n{extras[variant]}.\nHighly dimensional, realistic, memorable focal subject.\nLONG: keep lower 18–22% relatively clean for future spectrum.\nSHORT: prioritize mobile readability.\nDo NOT render 3D GOKIL, title text, spectrum, equalizer, watermark, or random text into the image."""


def seo(dna_name, title, story, target):
    d = MUSIC_DNAS[dna_name]
    kws = [title, dna_name, "musik Indonesia", "lagu Indonesia", "3D GOKIL"] + d["topics"][:5]
    desc = f"{title} — 3D GOKIL\n\nMusic DNA: {dna_name}\n\n{story['body']}\n\n{d['desc']}\n\nTarget: {target}\n\n#3DGOKIL #MusikIndonesia"
    return desc, ", ".join(dict.fromkeys(kws))


def get_secret(name):
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name)


def run_live_research(keyword, country, language, max_results=30):
    key = get_secret("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY belum dipasang di Streamlit Secrets.")

    try:
        from googleapiclient.discovery import build
    except Exception as e:
        raise RuntimeError(f"google-api-python-client belum terpasang: {e}")

    try:
        import research as r
    except Exception as e:
        raise RuntimeError(f"research.py tidak bisa dimuat: {e}")

    yt = build("youtube", "v3", developerKey=key)
    region = {"Indonesia": "ID", "United States": "US", "Malaysia": "MY", "Singapore": "SG", "Worldwide": None}[country]
    lang = {"Indonesian": "id", "English": "en", "Malay": "ms"}[language]

    ids = r.search_video_ids(yt, keyword, max_results, region, lang)
    if not ids:
        return []

    items = r.fetch_video_details(yt, ids)
    channel_ids = [item["snippet"]["channelId"] for item in items]
    channel_items = r.fetch_channel_details(yt, channel_ids)
    channel_map = {}

    for c in channel_items:
        stats = c.get("statistics", {})
        channel_map[c["id"]] = {
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "country": c.get("snippet", {}).get("country", ""),
        }

    rows = [r.metrics(item, channel_map) for item in items]
    rows.sort(key=lambda row: row.get("opportunity", 0), reverse=True)
    return rows


# ============================================================
# HEADER / SIDEBAR
# ============================================================

st.title("🔥 3D GOKIL AI MUSIC FACTORY")
st.caption("Brand tetap 3D GOKIL • Music DNA bisa berubah • Research → Story → Title → Lyric → Suno → Artwork → SEO → Export")

with st.sidebar:
    st.header("🧬 MUSIC DNA")
    dna_options = list(MUSIC_DNAS.keys())
    dna_index = dna_options.index(st.session_state.dna)
    selected_dna = st.selectbox("Pilih DNA Musik", dna_options, index=dna_index, key="dna_selector")
    if selected_dna != st.session_state.dna:
        st.session_state.dna = selected_dna
        st.session_state.stories = []
        st.session_state.story_i = 0
        st.session_state.titles = []
        st.session_state.final_title = ""
        st.session_state.lyrics = ""
        st.session_state.research_results = []
        st.rerun()

    st.success(st.session_state.dna)
    st.caption(D()["desc"])

    target_options = ["Indonesia", "Indonesia + Global", "Global"]
    target_index = target_options.index(st.session_state.target)
    st.session_state.target = st.selectbox("🎯 Target Audience", target_options, index=target_index, key="target_selector")

    tone_options = ["Auto", "Emotional", "Energetic", "Rebellious", "Dark", "Chill"]
    tone_index = tone_options.index(st.session_state.tone)
    st.session_state.tone = st.selectbox("🎭 Tone", tone_options, index=tone_index, key="tone_selector")

    st.divider()
    st.write("**SHORT:** discovery / subscriber")
    st.write("**LONG:** full song / watch time")

with st.expander("🧬 DNA DASHBOARD", expanded=True):
    d = D()
    st.markdown(
        f"**🎵 Music DNA:** {st.session_state.dna}\n\n"
        f"**❤️ Emotion:** {d['emo']}\n\n"
        f"**🎯 Target:** {st.session_state.target}\n\n"
        f"**📦 Output:** SHORT + LONG"
    )
    st.write("**Audience:**", d["aud"])
    st.write("**Core topics:**", " • ".join(d["topics"]))

# ============================================================
# MOBILE MENU
# ============================================================

page = st.selectbox("📂 MENU", PAGES, index=PAGES.index(st.session_state.page), key="page_selector")
st.session_state.page = page

# ============================================================
# RESEARCH
# ============================================================

if page == "🔎 RESEARCH":
    st.header("🔎 Audience & Trend Research")
    st.write("Riset mengikuti Music DNA aktif, target negara, dan keyword. Data live diambil dari YouTube Data API melalui research.py.")

    keyword = st.text_input("Keyword / topik riset", value=D()["topics"][0], key="research_keyword")
    country = st.selectbox("Negara target", ["Indonesia", "United States", "Malaysia", "Singapore", "Worldwide"], key="research_country")
    language = st.selectbox("Bahasa", ["Indonesian", "English", "Malay"], key="research_language")

    api_ready = bool(get_secret("YOUTUBE_API_KEY"))
    st.info("🟢 YOUTUBE_API_KEY terbaca di Streamlit Secrets." if api_ready else "🔴 YOUTUBE_API_KEY belum terbaca. Tambahkan di Streamlit → Manage app → Settings/Secrets.")

    if st.button("🔎 ANALISIS PELUANG", use_container_width=True):
        if not api_ready:
            st.error("YOUTUBE_API_KEY belum tersedia di Streamlit Secrets.")
        else:
            with st.spinner("Mengambil data YouTube dan menghitung opportunity score..."):
                try:
                    st.session_state.research_results = run_live_research(keyword, country, language, 30)
                    st.session_state.research_meta = {
                        "keyword": keyword,
                        "country": country,
                        "language": language,
                        "time": datetime.now().isoformat(timespec="seconds"),
                    }
                except Exception as exc:
                    st.error(f"Riset gagal: {exc}")

    rows = st.session_state.research_results
    if rows:
        meta = st.session_state.research_meta
        st.success(f"Riset selesai: {meta.get('keyword')} • {meta.get('country')} • {len(rows)} video")
        st.subheader("🔥 Top Opportunities")
        for i, row in enumerate(rows[:15], 1):
            st.markdown(f"**{i}. [{row.get('opportunity', 0):.0f}] {row.get('title', '')}**")
            st.caption(
                f"{row.get('trend', '')} • {row.get('channel_name', '')} • "
                f"Views {row.get('views', 0):,} • Subs {row.get('subscribers', 0):,} • "
                f"View/Sub {row.get('view_sub', 0):.1f}x • Views/Day {row.get('views_day', 0):,.0f} • "
                f"Eng {row.get('engagement', 0):.2f}%"
            )

# ============================================================
# STORY
# ============================================================

elif page == "🎭 STORY":
    st.header("🎭 Story / Theme Lab")
    sub_options = CATS.get(st.session_state.dna, [])
    if not sub_options:
        st.error("Kategori untuk DNA aktif tidak ditemukan.")
    else:
        sub = st.selectbox("Sub-theme", sub_options, key="story_subtheme")
        custom = st.text_input("Sub-theme custom (opsional)", key="story_custom")
        chosen_sub = custom.strip() or sub

        if st.button("🔥 GENERATE 10 STORY", use_container_width=True):
            st.session_state.stories = build_stories(st.session_state.dna, chosen_sub)
            st.session_state.story_i = 0
            st.session_state.titles = []
            st.session_state.final_title = ""
            st.session_state.lyrics = ""
            st.success("10 story berhasil dibuat.")

        if st.session_state.stories:
            for i, story in enumerate(st.session_state.stories):
                with st.container(border=True):
                    st.markdown(f"### {i + 1:02d}. {story['title']}")
                    st.write(story["body"])
                    st.caption(f"🎭 {story['emotion']} | 🎣 {story['hook']}")
                    if st.button(f"👉 PILIH STORY {i + 1:02d}", key=f"story_pick_{i}"):
                        st.session_state.story_i = i
                        st.session_state.titles = []
                        st.session_state.final_title = ""
                        st.session_state.lyrics = ""
                        st.rerun()

            idx = min(max(st.session_state.story_i, 0), len(st.session_state.stories) - 1)
            st.session_state.story_i = idx
            st.success("Story aktif: " + st.session_state.stories[idx]["title"])
        else:
            st.info("Pilih sub-theme lalu tekan GENERATE 10 STORY.")

# ============================================================
# TITLE
# ============================================================

elif page == "🎯 TITLE":
    st.header("🎯 Title Lab")
    if not st.session_state.stories:
        st.info("Pilih Story terlebih dahulu.")
    else:
        idx = min(st.session_state.story_i, len(st.session_state.stories) - 1)
        story = st.session_state.stories[idx]
        if st.button("🚀 GENERATE TITLE OPTIONS", use_container_width=True):
            st.session_state.titles = make_titles(story, st.session_state.dna, st.session_state.target, st.session_state.tone)

        for i, title in enumerate(sorted(st.session_state.titles, key=score_title, reverse=True)):
            st.markdown(f"**{i + 1}. {title}** — `{score_title(title)}/50`")
            if st.button(f"USE #{i + 1}", key=f"title_pick_{i}"):
                st.session_state.final_title = title
        if st.session_state.final_title:
            st.success("🔥 " + st.session_state.final_title)

# ============================================================
# LYRIC
# ============================================================

elif page == "✍️ LYRIC":
    st.header("✍️ Lyric Lab")
    if not st.session_state.stories:
        st.info("Pilih Story terlebih dahulu.")
    else:
        idx = min(st.session_state.story_i, len(st.session_state.stories) - 1)
        story = st.session_state.stories[idx]
        title = st.text_input("Judul lagu", value=st.session_state.final_title or story["title"], key="lyric_title")
        if st.button("🎤 GENERATE LYRICS", use_container_width=True):
            st.session_state.lyrics = make_lyrics(title, story, st.session_state.dna)
        st.session_state.lyrics = st.text_area("Lyrics — editable", value=st.session_state.lyrics, height=520, key="lyrics_editor")

# ============================================================
# SUNO
# ============================================================

elif page == "🎸 SUNO":
    st.header("🎸 Suno Style — DNA Aktif")
    style = suno(st.session_state.dna)
    st.code(style, language="text")
    st.download_button("⬇️ DOWNLOAD SUNO STYLE", style, file_name=f"{slug(st.session_state.dna)}_suno.txt", mime="text/plain")

# ============================================================
# ARTWORK
# ============================================================

elif page == "🖼️ ARTWORK":
    st.header("🖼️ Artwork Lab — 5 konsep")
    if st.session_state.stories:
        idx = min(st.session_state.story_i, len(st.session_state.stories) - 1)
        story = st.session_state.stories[idx]
    else:
        story = {"title": "JUDUL LAGU", "body": D()["desc"], "hook": ""}
    title = st.session_state.final_title or story["title"]

    variants = ["Cinematic", "GOKIL / Absurd", "Dark / Mystical", "Social / Relatable", "Stop-scroll"]
    for variant in variants:
        st.subheader(variant)
        st.markdown("**LONG — 16:9**")
        st.code(artwork(st.session_state.dna, title, story, "16:9", variant), language="text")
        st.markdown("**SHORT — 9:16**")
        st.code(artwork(st.session_state.dna, title, story, "9:16", variant), language="text")

# ============================================================
# SEO
# ============================================================

elif page == "🚀 SEO":
    st.header("🚀 YouTube SEO")
    if st.session_state.stories:
        idx = min(st.session_state.story_i, len(st.session_state.stories) - 1)
        story = st.session_state.stories[idx]
    else:
        story = {"title": "JUDUL LAGU", "body": D()["desc"]}
    title = st.session_state.final_title or story["title"]
    desc, keywords = seo(st.session_state.dna, title, story, st.session_state.target)
    st.text_input("YouTube Title", value=title)
    st.text_area("Description", value=desc, height=280)
    st.text_input("Keywords", value=keywords)
    st.text_input("Hashtags", value=f"#3DGOKIL #{slug(st.session_state.dna).replace('_', '')} #MusikIndonesia")

# ============================================================
# EXPORT
# ============================================================

else:
    st.header("📦 Export Project Metadata")
    if st.session_state.stories:
        idx = min(st.session_state.story_i, len(st.session_state.stories) - 1)
        story = st.session_state.stories[idx]
    else:
        story = {"title": "JUDUL LAGU", "body": D()["desc"], "hook": ""}
    title = st.session_state.final_title or story["title"]
    meta = {
        "brand": BRAND,
        "music_dna": st.session_state.dna,
        "target": st.session_state.target,
        "tone": st.session_state.tone,
        "story": story,
        "title": title,
        "lyrics": st.session_state.lyrics,
        "suno_style": suno(st.session_state.dna),
        "artwork_long_prompt": artwork(st.session_state.dna, title, story, "16:9", "Cinematic"),
        "artwork_short_prompt": artwork(st.session_state.dna, title, story, "9:16", "Stop-scroll"),
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "strategy": {"long": "full song / watch time", "short": "discovery / subscriber"},
    }
    st.json(meta)
    st.download_button(
        "⬇️ DOWNLOAD PROJECT JSON",
        json.dumps(meta, ensure_ascii=False, indent=2),
        file_name=f"{slug(title)}_project.json",
        mime="application/json",
        use_container_width=True,
    )

st.divider()
st.caption("🔥 3D GOKIL AI MUSIC FACTORY • Brand tetap • Music DNA fleksibel")
