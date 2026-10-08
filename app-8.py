import os
import re
import math
from collections import Counter, defaultdict

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="3D GOKIL AI CONTENT FACTORY",
    page_icon="🔥",
    layout="wide",
)

# =========================================================
# SAFE YOUTUBE SECRET BRIDGE
# =========================================================
try:
    if "YOUTUBE_API_KEY" in st.secrets and st.secrets["YOUTUBE_API_KEY"]:
        os.environ["YOUTUBE_API_KEY"] = str(st.secrets["YOUTUBE_API_KEY"]).strip()
except Exception:
    pass

try:
    import research
    RESEARCH_IMPORT_ERROR = None
except Exception as e:
    research = None
    RESEARCH_IMPORT_ERROR = str(e)

# =========================================================
# UNIVERSAL CONTENT DNA
# =========================================================
MODE_LIBRARY = {
    "🎵 Music": {
        "niche": "Music",
        "audience": "pendengar musik sesuai genre dan tema",
        "formats": "song / lyric / music video / Shorts",
        "script_name": "LYRIC",
        "seed_templates": [
            "music {topic}", "lagu {topic}", "musik {topic}",
            "{topic} indonesia", "{topic} song"
        ],
    },
    "🧒 Cerita Anak": {
        "niche": "Kids / Children Stories",
        "audience": "anak dan orang tua",
        "formats": "story / narration / animation / Shorts",
        "script_name": "STORY SCRIPT",
        "seed_templates": [
            "cerita anak {topic}", "dongeng {topic}", "cerita sebelum tidur {topic}",
            "kids story {topic}", "children story {topic}"
        ],
    },
    "🌍 Berita Dunia": {
        "niche": "News / Current Affairs",
        "audience": "penonton yang mencari informasi dan konteks",
        "formats": "news explainer / commentary / Shorts",
        "script_name": "NEWS SCRIPT",
        "seed_templates": [
            "berita dunia {topic}", "world news {topic}", "latest news {topic}",
            "{topic} explained", "{topic} update"
        ],
    },
    "👻 Horror": {
        "niche": "Horror / Mystery",
        "audience": "penonton horror, misteri, dan cerita seram",
        "formats": "horror story / narration / Shorts",
        "script_name": "HORROR SCRIPT",
        "seed_templates": [
            "cerita horor {topic}", "kisah misteri {topic}", "horror story {topic}",
            "true horror {topic}", "misteri {topic}"
        ],
    },
    "🎮 Gaming": {
        "niche": "Gaming",
        "audience": "pemain dan penonton game sesuai judul/platform",
        "formats": "gameplay / guide / commentary / Shorts",
        "script_name": "VIDEO SCRIPT",
        "seed_templates": [
            "game {topic}", "{topic} gameplay", "{topic} guide",
            "{topic} tips", "{topic} shorts"
        ],
    },
    "📚 Education": {
        "niche": "Education",
        "audience": "pelajar dan penonton yang ingin belajar",
        "formats": "explainer / tutorial / Shorts",
        "script_name": "EXPLAINER SCRIPT",
        "seed_templates": [
            "belajar {topic}", "cara {topic}", "{topic} explained",
            "tutorial {topic}", "{topic} untuk pemula"
        ],
    },
    "😂 Comedy": {
        "niche": "Comedy",
        "audience": "penonton hiburan dan comedy",
        "formats": "sketch / commentary / Shorts",
        "script_name": "COMEDY SCRIPT",
        "seed_templates": [
            "komedi {topic}", "lucu {topic}", "comedy {topic}",
            "funny {topic}", "sketsa {topic}"
        ],
    },
    "🧩 Custom": {
        "niche": "Custom",
        "audience": "ditentukan oleh Creative DNA",
        "formats": "ditentukan oleh DNA",
        "script_name": "SCRIPT",
        "seed_templates": [
            "{topic}", "{topic} indonesia", "{topic} explained",
            "{topic} ideas", "{topic} shorts"
        ],
    },
}

COUNTRIES = {
    "Indonesia": ("ID", "id"),
    "United States": ("US", "en"),
    "United Kingdom": ("GB", "en"),
    "Malaysia": ("MY", "ms"),
    "Singapore": ("SG", "en"),
    "Philippines": ("PH", "en"),
    "India": ("IN", "en"),
    "Australia": ("AU", "en"),
    "Canada": ("CA", "en"),
    "Japan": ("JP", "ja"),
    "Germany": ("DE", "de"),
    "Global / Worldwide": (None, "en"),
}

DEFAULT_DNA = "REALITA KEHIDUPAN INDONESIA — cerita nyata, relatable, sedikit satire, emosional, dan menghibur."

# =========================================================
# HELPERS
# =========================================================
def infer_mode(dna: str) -> str:
    t = (dna or "").lower()
    rules = [
        (["musik", "music", "lagu", "song", "suno", "rock", "dangdut", "metal"], "🎵 Music"),
        (["anak", "kids", "children", "dongeng", "nursery", "cerita anak"], "🧒 Cerita Anak"),
        (["berita", "news", "politik", "dunia", "current affairs", "geopolitik"], "🌍 Berita Dunia"),
        (["horor", "horror", "misteri", "seram", "ghost", "paranormal"], "👻 Horror"),
        (["gaming", "game", "esports", "mobile legends", "minecraft", "roblox"], "🎮 Gaming"),
        (["belajar", "education", "edukasi", "tutorial", "sejarah", "sains", "science"], "📚 Education"),
        (["komedi", "comedy", "lucu", "humor", "funny", "satire"], "😂 Comedy"),
    ]
    for words, mode in rules:
        if any(w in t for w in words):
            return mode
    return "🧩 Custom"


def clean_topic(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    return text[:90]


def topic_from_dna(dna: str, mode: str) -> str:
    """Create a useful research seed from free-form DNA without pretending it is search volume."""
    dna = clean_topic(dna)
    if not dna:
        return ""
    # Remove common identity words that are poor search seeds.
    t = re.sub(r"\b(creative|content|dna|channel|brand|realita kehidupan)\b", " ", dna, flags=re.I)
    t = re.sub(r"[—|/:]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if not t:
        t = dna
    return t[:70]


def auto_seed_keywords(dna: str, mode: str, custom_keyword: str = ""):
    cfg = MODE_LIBRARY[mode]
    topic = clean_topic(custom_keyword) or topic_from_dna(dna, mode)
    if not topic:
        topic = cfg["niche"]
    seeds = []
    for template in cfg["seed_templates"]:
        q = template.format(topic=topic).strip()
        if q and q.lower() not in [x.lower() for x in seeds]:
            seeds.append(q)
    # Add the raw DNA/topic as a direct search signal.
    for q in [topic, clean_topic(dna)]:
        if q and q.lower() not in [x.lower() for x in seeds]:
            seeds.append(q)
    return seeds[:6]


def safe_num(v, default=0):
    try:
        return float(v)
    except Exception:
        return default


def fmt_num(v):
    v = safe_num(v)
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.1f}M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.1f}K"
    return f"{int(v):,}"


def normalize_research_rows(result):
    rows = []
    for r in result.get("videos", []) or []:
        rows.append({
            "Opportunity": int(r.get("score", 0)),
            "Trend": r.get("trend", "-"),
            "Channel": r.get("channel", "-"),
            "Title": r.get("title", "-"),
            "Views": int(r.get("views", 0)),
            "Subscribers": int(r.get("subs", 0)),
            "View/Sub": round(safe_num(r.get("vs")), 1),
            "Views/Day": round(safe_num(r.get("vpd"))),
            "Engagement %": round(safe_num(r.get("eng")), 3),
            "Format": r.get("duration", 0) <= 60 and "Shorts" or "Long-form",
        })
    return rows


def keyword_candidates(result, seeds, mode="🧩 Custom", dna=""):
    rows = result.get("videos", []) or []
    seed_words = set()
    for s in seeds:
        for w in re.findall(r"[\w-]+", s.lower()):
            if len(w) >= 3:
                seed_words.add(w)

    stop = {
        "the", "and", "for", "with", "from", "this", "that", "video", "official",
        "full", "live", "best", "new", "2024", "2025", "2026", "2027", "shorts",
        "yang", "dan", "untuk", "dengan", "dari", "ini", "itu", "lagu", "versi",
        "terbaik", "indonesia", "music", "musik", "story", "cerita", "news", "berita",
        "viral", "terbaru", "saat", "aku", "kita", "dia", "the", "you",
    }

    # Mode-specific vocabulary prevents unrelated terms (mis. anak/balita)
    # from becoming the active keyword when the user is researching Music.
    mode_terms = {
        "🎵 Music": {"lagu", "musik", "song", "music", "rock", "metal", "dangdut", "koplo", "pop", "indie", "band", "penyanyi", "lirik", "album", "soundtrack"},
        "🧒 Cerita Anak": {"anak", "balita", "dongeng", "cerita", "kids", "children", "bayi", "petualangan", "moral"},
        "🌍 Berita Dunia": {"berita", "news", "dunia", "world", "politik", "konflik", "update", "explained", "presiden", "ekonomi"},
        "👻 Horror": {"horor", "horror", "misteri", "seram", "ghost", "hantu", "paranormal", "creepy"},
        "🎮 Gaming": {"game", "gaming", "gameplay", "guide", "tips", "minecraft", "roblox", "esports"},
        "📚 Education": {"belajar", "edukasi", "education", "tutorial", "cara", "sejarah", "sains", "science", "pemula"},
        "😂 Comedy": {"komedi", "comedy", "lucu", "humor", "funny", "sketsa", "satire", "jokes"},
    }
    allowed = mode_terms.get(mode, set())
    dna_words = {w for w in re.findall(r"[\w-]+", (dna or "").lower()) if len(w) >= 4 and w not in stop}
    stats = defaultdict(lambda: {"weight": 0.0, "count": 0, "views": 0, "vpd": 0.0, "score": 0.0, "titles": []})

    for r in rows:
        title = r.get("title", "")
        words = [w for w in re.findall(r"[\w-]+", title.lower()) if len(w) >= 3 and w not in stop]
        score = safe_num(r.get("score"))
        weight = max(score, 1)
        for w in words:
            if w in seed_words or w in stop:
                continue
            # Keep only terms that are connected to the selected content mode,
            # the Creative DNA, or a strong multi-video signal.
            mode_match = bool(allowed & {w})
            dna_match = w in dna_words
            if mode in mode_terms and not (mode_match or dna_match):
                continue
            d = stats[w]
            d["weight"] += weight * (1.35 if mode_match else 1.15 if dna_match else 0.55)
            d["count"] += 1
            d["views"] += safe_num(r.get("views"))
            d["vpd"] += safe_num(r.get("vpd"))
            d["score"] += score
            if len(d["titles"]) < 3:
                d["titles"].append(title)

        # Useful 2-word phrases from titles.
        for a, b in zip(words, words[1:]):
            phrase = f"{a} {b}"
            if a in seed_words or b in seed_words:
                continue
            if a in stop or b in stop:
                continue
            if mode in mode_terms and not ((a in allowed or b in allowed) or a in dna_words or b in dna_words):
                continue
            d = stats[phrase]
            d["weight"] += weight * 1.35
            d["count"] += 1
            d["views"] += safe_num(r.get("views"))
            d["vpd"] += safe_num(r.get("vpd"))
            d["score"] += score
            if len(d["titles"]) < 3:
                d["titles"].append(title)

    ranked = []
    for kw, d in stats.items():
        if d["count"] < 1:
            continue
        raw = d["weight"] + math.log10(max(d["views"], 10)) * 2
        ranked.append({
            "Keyword": kw,
            "Signal": round(raw, 1),
            "Evidence": d["count"],
            "Avg Opportunity": round(d["score"] / max(d["count"], 1), 1),
            "Views Evidence": int(d["views"]),
            "Views/Day Evidence": int(d["vpd"]),
            "Examples": " | ".join(d["titles"]),
        })
    ranked.sort(key=lambda x: (x["Signal"], x["Avg Opportunity"]), reverse=True)
    return ranked[:20]


def run_auto_research(dna, mode, country_name, custom_keyword, max_per_keyword=15):
    if research is None:
        raise RuntimeError(f"research.py tidak bisa dimuat: {RESEARCH_IMPORT_ERROR}")
    if "YOUTUBE_API_KEY" not in os.environ or not os.environ.get("YOUTUBE_API_KEY"):
        raise RuntimeError("YOUTUBE_API_KEY belum terbaca. Isi Streamlit Secrets dengan YOUTUBE_API_KEY = \"API_KEY\".")

    region, language = COUNTRIES[country_name]
    seeds = auto_seed_keywords(dna, mode, custom_keyword)
    query_text = ", ".join(seeds)
    result = research.research(
        query_text,
        country=region,
        language=language,
        max_per_keyword=max_per_keyword,
    )
    result["auto_seeds"] = seeds
    result["country_name"] = country_name
    result["mode"] = mode
    result["keyword_candidates"] = keyword_candidates(result, seeds, mode, dna)
    return result


def title_candidates(mode, keyword, dna):
    k = keyword.strip() or "TOPIK UTAMA"
    mode_title = MODE_LIBRARY[mode]["niche"]
    if mode == "🎵 Music":
        return [
            k.upper(), f"{k.upper()} — CERITA YANG KITA RASAKAN",
            f"{k.upper()} | LAGU UNTUK YANG SEDANG BERTAHAN",
            f"{k.upper()} — JANGAN PURA-PURA KUAT",
            f"{k.upper()} | INDONESIAN REAL LIFE",
            f"{k.upper()} — SAAT HIDUP TIDAK SESUAI RENCANA",
        ]
    if mode == "🧒 Cerita Anak":
        return [
            f"{k.title()} — Petualangan Seru",
            f"Kisah {k.title()} yang Mengajarkan Keberanian",
            f"{k.title()} dan Rahasia yang Tak Terduga",
            f"Dongeng {k.title()} Sebelum Tidur",
            f"Apa yang Terjadi pada {k.title()}?",
        ]
    if mode == "🌍 Berita Dunia":
        return [
            f"{k.title()}: Apa yang Sebenarnya Terjadi?",
            f"{k.title()} Dijelaskan dalam 5 Menit",
            f"Update {k.title()} — Dampaknya ke Dunia",
            f"Kenapa {k.title()} Penting?",
            f"{k.title()}: Fakta, Kronologi, dan Dampaknya",
        ]
    if mode == "👻 Horror":
        return [
            f"{k.title()} — Jangan Dengar Sendirian",
            f"Misteri {k.title()} yang Tidak Terjawab",
            f"Kisah {k.title()} — Ada yang Mengikuti",
            f"{k.title()}: Cerita yang Seharusnya Tidak Dibuka",
            f"Apa yang Terjadi Malam Itu? {k.title()}",
        ]
    if mode == "🎮 Gaming":
        return [
            f"{k.title()} — Tips yang Wajib Dicoba",
            f"{k.title()} Gameplay: Cara Menang Lebih Cepat",
            f"5 Kesalahan Pemain {k.title()}",
            f"{k.title()} — Guide untuk Pemula",
            f"Rahasia {k.title()} yang Jarang Diketahui",
        ]
    if mode == "📚 Education":
        return [
            f"{k.title()} Dijelaskan dengan Mudah",
            f"Belajar {k.title()} dari Nol",
            f"{k.title()} dalam 5 Menit",
            f"Kesalahan Umum Saat Belajar {k.title()}",
            f"Cara Memahami {k.title()} Tanpa Ribet",
        ]
    if mode == "😂 Comedy":
        return [
            f"Kalau {k.title()} Jadi Masalah Sehari-hari",
            f"{k.title()} Tapi Dibuat GOKIL",
            f"Ekspektasi vs Realita: {k.title()}",
            f"Ketika {k.title()} Sudah Tidak Masuk Akal",
            f"POV: Kamu Menghadapi {k.title()}",
        ]
    return [
        f"{k.title()} — Sudut Pandang yang Berbeda",
        f"{k.title()} Dijelaskan Tanpa Ribet",
        f"Realita di Balik {k.title()}",
        f"Apa yang Sebenarnya Terjadi pada {k.title()}?",
        f"{k.title()} — Cerita yang Jarang Dibahas",
    ]


def make_script(mode, title, keyword, dna):
    if mode == "🎵 Music":
        return f"""[INTRO / AUDIO HOOK 0:00–0:05]\n{title.upper()}!\n\n[VERSE 1]\nTentang {keyword}, tentang hari yang kita jalani,\nada yang tertahan, ada yang belum selesai.\n\n[PRE-CHORUS]\nKalau dunia terus menekan,\nkita tetap punya alasan untuk berjalan.\n\n[CHORUS]\n{title.upper()}\nKita jatuh, kita bangkit lagi,\nmeski berat, kita tetap di sini.\n\n[VERSE 2]\nRealita datang tanpa aba-aba,\ntapi cerita kita belum selesai.\n\n[BRIDGE]\nTarik napas. Lihat ke depan.\nKita masih punya suara.\n\n[FINAL CHORUS]\n{title.upper()}\nBelum selesai — GAS LAGI!\n\n[OUTRO]\n{keyword}..."""
    if mode == "🧒 Cerita Anak":
        return f"""[OPENING]\nSuatu hari, {keyword} mengalami sesuatu yang sangat aneh...\n\n[SETUP]\nTokoh utama menemukan masalah yang belum pernah ia lihat sebelumnya.\nIa harus memilih antara menyerah atau mencoba.\n\n[ADVENTURE]\nPerjalanan dimulai. Ada rintangan, teman baru, dan satu rahasia.\n\n[LESSON]\nKeberanian bukan berarti tidak takut. Keberanian berarti tetap mencoba.\n\n[ENDING]\nMasalah selesai, tetapi petualangan baru saja dimulai."""
    if mode == "🌍 Berita Dunia":
        return f"""[HOOK]\nApa yang sebenarnya terjadi dengan {keyword}?\n\n[CONTEXT]\nJelaskan kejadian utama dengan tanggal, lokasi, dan pihak yang terlibat.\n\n[WHAT HAPPENED]\nSusun kronologi berdasarkan sumber yang dapat diverifikasi.\n\n[WHY IT MATTERS]\nTerangkan dampak terhadap masyarakat, ekonomi, keamanan, atau kebijakan.\n\n[WHAT NEXT]\nJelaskan perkembangan berikutnya dan apa yang masih belum diketahui.\n\n[DISCLAIMER]\nBedakan fakta, pernyataan pihak terkait, dan analisis."""
    if mode == "👻 Horror":
        return f"""[HOOK]\nJangan matikan lampu sebelum cerita {keyword} selesai.\n\n[SETUP]\nTokoh utama menemukan sesuatu yang tidak seharusnya ada.\n\n[ESCALATION]\nHal kecil berubah menjadi pola yang semakin mengganggu.\n\n[REVEAL]\nSatu petunjuk mengubah seluruh arti kejadian.\n\n[ENDING]\nDan sejak malam itu, tidak ada yang benar-benar sama."""
    if mode == "🎮 Gaming":
        return f"""[HOOK]\nKalau kamu masih melakukan ini di {keyword}, berhenti dulu.\n\n[PROBLEM]\nKesalahan paling umum pemain.\n\n[SOLUTION]\nLangkah 1 — setup.\nLangkah 2 — timing.\nLangkah 3 — eksekusi.\n\n[PAYOFF]\nTunjukkan hasil sebelum dan sesudah.\n\n[CTA]\nCoba sendiri dan bandingkan hasilnya."""
    if mode == "📚 Education":
        return f"""[HOOK]\n{keyword} sebenarnya tidak serumit yang kamu kira.\n\n[CONCEPT]\nJelaskan satu konsep utama dengan bahasa sederhana.\n\n[EXAMPLE]\nBerikan contoh kehidupan nyata.\n\n[COMMON MISTAKE]\nTunjukkan kesalahan yang sering terjadi.\n\n[RECAP]\nRangkum tiga poin utama dalam kalimat singkat."""
    if mode == "😂 Comedy":
        return f"""[SETUP]\nKita semua pernah menghadapi {keyword}.\n\n[EXPECTATION]\nSemua terlihat mudah.\n\n[REALITY]\nTernyata hidup punya rencana lain.\n\n[ESCALATION]\nMasalah kecil berubah menjadi masalah yang terlalu serius.\n\n[PUNCHLINE]\nAkhirnya kita sadar: ternyata masalahnya bukan {keyword}. Masalahnya kita terlalu percaya diri."""
    return f"""[HOOK]\nKenapa {keyword} penting untuk dibahas?\n\n[CONTEXT]\nBerikan konteks singkat.\n\n[MAIN POINT]\nJelaskan satu ide utama dengan contoh konkret.\n\n[PAYOFF]\nBerikan sudut pandang yang berbeda dan mudah diingat.\n\n[ENDING]\nTutup dengan satu kalimat yang membuat penonton ingin tahu lebih jauh."""


def style_prompt(mode, dna, keyword):
    if mode == "🎵 Music":
        return "Modern Indonesian rock/dangdut with emotional vocal, immediate audio hook, strong chorus, tight drums/kendang, cinematic atmosphere, clear bass, memorable melody, no long intro, original arrangement."
    if mode == "🧒 Cerita Anak":
        return "Warm playful children's storytelling, clear narration, gentle music, colorful sound design, simple language, positive emotional arc, family-safe, memorable ending."
    if mode == "🌍 Berita Dunia":
        return "Clear journalistic explainer style, calm authoritative narration, concise pacing, visual timeline, maps/charts where useful, distinguish verified facts from analysis, no sensationalism."
    if mode == "👻 Horror":
        return "Dark cinematic horror atmosphere, slow tension build, intimate narration, subtle ambient sound, restrained jump scares, mysterious visual storytelling, unsettling but coherent ending."
    if mode == "🎮 Gaming":
        return "Fast-paced gaming commentary, clear step-by-step explanation, energetic delivery, on-screen highlights, concise edits, immediate payoff."
    if mode == "📚 Education":
        return "Clean educational explainer, simple language, visual examples, structured progression, friendly narration, one concept at a time, strong recap."
    if mode == "😂 Comedy":
        return "Fast relatable comedy, clear setup, escalating absurdity, short pauses for timing, strong punchline, family-safe unless explicitly changed."
    return f"Original content style based on Creative DNA: {dna}. Topic: {keyword}. Keep the identity consistent and the format easy to understand."


def artwork_prompts(mode, title, keyword, dna):
    base = f"Topic: {keyword}. Title: {title}. Creative DNA: {dna}."
    concepts = [
        ("01 — CINEMATIC REALISM", "High-end cinematic visual, realistic depth, strong focal subject, dramatic lighting, storytelling composition, premium detail, no clutter."),
        ("02 — ABSURD / GOKIL", "Unexpected visual metaphor, humorous but intelligent, dimensional 3D look, exaggerated situation, instantly understandable at thumbnail size."),
        ("03 — DARK / MYSTICAL", "Dark atmospheric world, mystery, volumetric light, deep shadows, symbolic objects, strong contrast, cinematic depth."),
        ("04 — SOCIAL / HUMAN", "Human-centered visual, authentic emotion, everyday environment, relatable character, subtle social message, realistic cinematic texture."),
        ("05 — STOP-SCROLL EXPERIMENTAL", "Bold unconventional composition, extreme focal point, visual curiosity, high contrast, unusual scale relationship, designed to stop scrolling."),
    ]
    out = []
    for name, desc in concepts:
        out.append((name, f"{base}\n{desc}\n16:9 long-form artwork, no logo, no watermark, no unnecessary text."))
    return out


def seo_package(mode, title, keyword, dna):
    tags = [keyword, MODE_LIBRARY[mode]["niche"], "youtube", "shorts"]
    if mode == "🎵 Music":
        tags += ["musik indonesia", "lagu indonesia"]
    elif mode == "🧒 Cerita Anak":
        tags += ["cerita anak", "dongeng"]
    elif mode == "🌍 Berita Dunia":
        tags += ["world news", "news update"]
    hashtags = " ".join("#" + re.sub(r"[^A-Za-z0-9]", "", x.title().replace(" ", "")) for x in tags[:6])
    description = f"{title}\n\nTopik: {keyword}\n\nCreative DNA: {dna}\nFormat: {MODE_LIBRARY[mode]['formats']}\n\n{hashtags}"
    return description, hashtags

# =========================================================
# SESSION STATE
# =========================================================
for key, default in {
    "research_result": None,
    "active_keyword": "",
    "selected_title": "",
    "script": "",
    "script_editor": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# =========================================================
# HEADER / SIDEBAR
# =========================================================
st.title("🔥 3D GOKIL AI CONTENT FACTORY")
st.caption("DNA → Audience → Auto Keyword → YouTube Research → Content Strategy → Title → Script/Lyric → Visual → SEO")

with st.sidebar:
    st.header("🧬 CREATIVE DNA")
    dna = st.text_area("Creative DNA", DEFAULT_DNA, height=100)
    mode_auto = infer_mode(dna)
    mode = st.selectbox("Content DNA / Mode", list(MODE_LIBRARY.keys()), index=list(MODE_LIBRARY.keys()).index(mode_auto))
    if st.button("🤖 AUTO MODE DARI DNA", use_container_width=True):
        mode = infer_mode(dna)
        st.session_state.auto_mode = mode
        st.rerun()
    country_name = st.selectbox("🎯 Target Country", list(COUNTRIES.keys()), index=0)
    st.caption(f"Mode terdeteksi: **{mode_auto}**")
    st.caption("DNA menentukan arah kreatif. Niche, keyword, format, dan output mengikuti mode.")

# =========================================================
# TABS
# =========================================================
tabs = st.tabs([
    "🌍 RESEARCH + AUTO KEYWORD",
    "💡 CONTENT IDEAS",
    "🎯 TITLE LAB",
    "✍️ SCRIPT / LYRIC",
    "🎨 STYLE + ARTWORK",
    "🚀 SEO",
])

# =========================================================
# RESEARCH + AUTO KEYWORD
# =========================================================
with tabs[0]:
    st.header("🌍 Audience & Trend Research")
    st.write("Satu tombol untuk mencari keyword awal, membaca video yang relevan, menghitung opportunity, lalu mengekstrak keyword dari pola judul.")

    custom_keyword = st.text_input(
        "Keyword dasar (opsional)",
        placeholder="Kosongkan jika ingin Factory mencari otomatis dari DNA",
    )
    max_per_keyword = st.slider("Video per keyword", 10, 30, 15, 5)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.info(f"**DNA:** {dna}\n\n**Mode:** {mode}\n\n**Target:** {country_name}")
    with c2:
        if st.button("🔥 CARI KEYWORD OTOMATIS", use_container_width=True, type="primary"):
            with st.spinner("Mencari sinyal keyword + riset YouTube..."):
                try:
                    result = run_auto_research(dna, mode, country_name, custom_keyword, max_per_keyword)
                    st.session_state.research_result = result
                    if result.get("keyword_candidates"):
                        st.session_state.active_keyword = result["keyword_candidates"][0]["Keyword"]
                    elif result.get("auto_seeds"):
                        st.session_state.active_keyword = result["auto_seeds"][0]
                    st.success(f"Riset selesai: {country_name} • {len(result.get('videos', []))} video")
                except Exception as e:
                    st.error(f"Riset gagal: {e}")

    result = st.session_state.research_result
    if result:
        st.subheader("🔎 Keyword yang dipakai Factory")
        st.write(" • ".join(result.get("auto_seeds", [])))

        st.subheader("🏆 AUTO KEYWORD FINDER — TOP SIGNAL")
        kw_rows = result.get("keyword_candidates", [])
        if kw_rows:
            kw_df = pd.DataFrame(kw_rows)
            st.dataframe(kw_df, use_container_width=True, hide_index=True)
            st.caption("Signal = skor internal dari kemunculan/pola judul + performa video yang ditemukan. Ini **bukan search volume resmi YouTube**.")
            choices = [x["Keyword"] for x in kw_rows]
            default_idx = choices.index(st.session_state.active_keyword) if st.session_state.active_keyword in choices else 0
            selected_kw = st.selectbox("Pilih keyword untuk Content Factory", choices, index=default_idx)
            if st.button("✅ GUNAKAN KEYWORD INI", use_container_width=True):
                st.session_state.active_keyword = selected_kw
                st.success(f"Keyword aktif: **{selected_kw}**")
        else:
            st.warning("Belum ada keyword kandidat dari hasil penelitian.")

        st.subheader("📊 TOP OPPORTUNITIES")
        rows = normalize_research_rows(result)
        if rows:
            top_df = pd.DataFrame(rows).sort_values(["Opportunity", "Views/Day"], ascending=False).head(15)
            st.dataframe(top_df, use_container_width=True, hide_index=True)
            st.caption("Mapping diperbaiki: Opportunity=score, Subscribers=subs, Views/Day=vpd, Engagement=eng.")

        st.subheader("🧬 Channel / Content DNA dari hasil riset")
        for i, item in enumerate(result.get("dna", [])[:8], 1):
            st.markdown(f"**{i}. {item.get('title','-')}** — {item.get('trend','-')} — {item.get('pattern','-')}")

        if result.get("phrases"):
            st.subheader("🧩 Frasa yang sering muncul")
            st.write(" • ".join(p[0] for p in result["phrases"][:15]))

        st.success(f"🎯 Keyword aktif sekarang: **{st.session_state.active_keyword or 'belum dipilih'}**")
    else:
        st.warning("Belum ada riset. Tekan **CARI KEYWORD OTOMATIS**.")

# =========================================================
# CONTENT IDEAS
# =========================================================
with tabs[1]:
    st.header("💡 Content Opportunity Lab")
    active_kw = st.session_state.get("active_keyword", "") or custom_keyword or topic_from_dna(dna, mode)
    st.markdown(f"**Keyword aktif:** `{active_kw}`")
    st.markdown(f"**Format:** {MODE_LIBRARY[mode]['formats']}  \n**Audience:** {MODE_LIBRARY[mode]['audience']}")

    result = st.session_state.research_result
    if result and result.get("ideas"):
        for i, idea in enumerate(result["ideas"][:5], 1):
            with st.container(border=True):
                st.markdown(f"### {i:02d}. {idea.get('title','Konsep')}")
                st.write(idea.get("angle", ""))
                st.caption(f"Format: {idea.get('format','-')} | Why: {idea.get('why','')}")
    else:
        st.info("Lakukan riset dulu agar Content Opportunity Lab memakai sinyal YouTube.")

    if st.button("💡 BUAT 10 ANGLE ORIGINAL", use_container_width=True):
        angles = [
            f"Masalah utama yang tersembunyi di balik {active_kw}",
            f"Kesalahan paling umum tentang {active_kw}",
            f"Hal yang jarang dibahas tentang {active_kw}",
            f"{active_kw}: ekspektasi vs realita",
            f"Cerita manusia di balik {active_kw}",
            f"{active_kw} untuk pemula",
            f"Apa yang berubah jika {active_kw} dilihat dari sudut berbeda?",
            f"5 fakta/pola penting tentang {active_kw}",
            f"Mitos vs fakta: {active_kw}",
            f"Prediksi / pelajaran berikutnya dari {active_kw}",
        ]
        st.session_state.angles = angles
    for i, angle in enumerate(st.session_state.get("angles", []), 1):
        st.markdown(f"**{i:02d}.** {angle}")

# =========================================================
# TITLE LAB
# =========================================================
with tabs[2]:
    st.header("🎯 Title Lab")
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    title_pool = title_candidates(mode, active_kw, dna)
    if st.button("🚀 GENERATE PILIHAN JUDUL", use_container_width=True):
        st.session_state.title_pool = title_pool
    for i, title in enumerate(st.session_state.get("title_pool", title_pool), 1):
        st.markdown(f"**{i}. {title}**")
        if st.button(f"✅ PILIH #{i}", key=f"pick_title_{i}"):
            st.session_state.selected_title = title
            st.success(f"Judul aktif: **{title}**")
    st.caption("Judul dibuat berdasarkan mode + keyword aktif. Opportunity research membantu arah topik, bukan jaminan viral.")

# =========================================================
# SCRIPT / LYRIC
# =========================================================
with tabs[3]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna)[0]
    st.header(f"✍️ {MODE_LIBRARY[mode]['script_name']} Lab")
    title_from_input = st.text_input("Judul aktif", value=active_title, key="script_title_input")
    if st.button("🎬 GENERATE SCRIPT / LYRIC", use_container_width=True):
        generated = make_script(mode, title_from_input, active_kw, dna)
        st.session_state.script = generated
        st.session_state.script_editor = generated
    st.text_area("Output editable", height=500, key="script_editor")
    st.session_state.script = st.session_state.get("script_editor", "")

# =========================================================
# STYLE + ARTWORK
# =========================================================
with tabs[4]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna)[0]
    st.header("🎨 Style + Artwork Lab")
    st.subheader("Style / Production Prompt")
    st.code(style_prompt(mode, dna, active_kw))
    st.subheader("🖼️ 5 Artwork / Visual Concepts")
    for name, prompt in artwork_prompts(mode, active_title, active_kw, dna):
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.code(prompt)
            st.caption("Gunakan konsep yang paling cocok dengan audience dan packaging channel.")

# =========================================================
# SEO
# =========================================================
with tabs[5]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna)[0]
    st.header("🚀 YouTube SEO")
    description, hashtags = seo_package(mode, active_title, active_kw, dna)
    st.text_input("YouTube Title", value=active_title, key="seo_title")
    st.text_area("Description", value=description, height=260, key="seo_description")
    st.text_input("Hashtags", value=hashtags, key="seo_hashtags")
    st.caption("SEO helper berfokus pada kejelasan topik dan packaging. Research signal bukan jaminan ranking.")

st.divider()
st.caption("3D GOKIL AI CONTENT FACTORY • Universal DNA Engine • Audience/Trend Research • Auto Keyword Finder")
