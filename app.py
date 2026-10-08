import os
import re
import math
import tempfile
from collections import Counter, defaultdict

import pandas as pd
import streamlit as st

try:
    import librosa
    import numpy as np
    AUDIO_IMPORT_ERROR = None
except Exception as e:
    librosa = None
    np = None
    AUDIO_IMPORT_ERROR = str(e)

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


# =========================================================
# MUSIC GENRE DNA — USER-CONTROLLED MIX
# =========================================================
MUSIC_GENRE_GROUPS = {
    "A — ROCK / METAL": ["Rock", "Hard Rock", "Heavy Metal", "Alternative Rock"],
    "B — DANGDUT / KOPLO": ["Dangdut", "Koplo", "Modern Dangdut", "Rock Dangdut"],
    "C — ELECTRONIC / CYBER": ["Electronic", "EDM", "Synthwave", "Cyberpunk"],
    "D — NUSANTARA / TRADITIONAL": ["Gamelan", "Suling Jawa", "Ethnic Fusion", "Indonesian Folk"],
    "E — POP / ALTERNATIVE": ["Pop", "Indie Pop", "Alternative", "Lo-fi"],
}

def selected_music_genre_text(groups):
    parts = []
    for g in groups or []:
        parts.extend(MUSIC_GENRE_GROUPS.get(g, [g]))
    return ", ".join(dict.fromkeys(parts))

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

LANGUAGE_LABELS = {
    "Indonesia": "Bahasa Indonesia",
    "United States": "English",
    "United Kingdom": "English",
    "Malaysia": "Bahasa Melayu",
    "Singapore": "English",
    "Philippines": "English",
    "India": "English",
    "Australia": "English",
    "Canada": "English",
    "Japan": "Japanese",
    "Germany": "German",
    "Global / Worldwide": "English",
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


def auto_seed_keywords(dna: str, mode: str, custom_keyword: str = "", country_name: str = "Indonesia", music_genres=None):
    cfg = MODE_LIBRARY[mode]
    topic = clean_topic(custom_keyword) or topic_from_dna(dna, mode)
    if not topic:
        topic = cfg["niche"]
    seeds = []
    for template in cfg["seed_templates"]:
        q = template.format(topic=topic).strip()
        # Never force Indonesia into searches when another target country is selected.
        if country_name != "Indonesia":
            q = re.sub(r"\s+indonesia\b", "", q, flags=re.I).strip()
        if q and q.lower() not in [x.lower() for x in seeds]:
            seeds.append(q)
    # Add target-country signal only when it is actually useful.
    if country_name == "Indonesia":
        localized = f"{topic} Indonesia"
    elif country_name == "Global / Worldwide":
        localized = topic
    else:
        localized = f"{topic} {country_name}"
    for q in [topic, localized, clean_topic(dna)]:
        if q and q.lower() not in [x.lower() for x in seeds]:
            seeds.append(q)
    if mode == "🎵 Music" and music_genres:
        genre_text = selected_music_genre_text(music_genres)
        for g in music_genres:
            for sub in MUSIC_GENRE_GROUPS.get(g, [g])[:2]:
                q = f"{topic} {sub}".strip()
                if country_name == "Indonesia":
                    q = f"{q} Indonesia"
                if q.lower() not in [x.lower() for x in seeds]:
                    seeds.append(q)
    return seeds[:10]


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


def run_auto_research(dna, mode, country_name, custom_keyword, max_per_keyword=15, music_genres=None):
    if research is None:
        raise RuntimeError(f"research.py tidak bisa dimuat: {RESEARCH_IMPORT_ERROR}")
    if "YOUTUBE_API_KEY" not in os.environ or not os.environ.get("YOUTUBE_API_KEY"):
        raise RuntimeError("YOUTUBE_API_KEY belum terbaca. Isi Streamlit Secrets dengan YOUTUBE_API_KEY = \"API_KEY\".")

    region, language = COUNTRIES[country_name]
    seeds = auto_seed_keywords(dna, mode, custom_keyword, country_name, music_genres)
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


def title_candidates(mode, keyword, dna, music_genres=None):
    k = keyword.strip() or "TOPIK UTAMA"
    mode_title = MODE_LIBRARY[mode]["niche"]
    if mode == "🎵 Music":
        gtxt = selected_music_genre_text(music_genres)
        suffix = f" ({gtxt})" if gtxt else ""
        return [
            f"{k.upper()}{suffix}",
            f"{k.upper()} — CERITA YANG KITA RASAKAN",
            f"{k.upper()} | LAGU UNTUK YANG SEDANG BERTAHAN",
            f"{k.upper()} — JANGAN PURA-PURA KUAT",
            f"{k.upper()} | REAL LIFE SONG",
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


def make_script(mode, title, keyword, dna, language="Bahasa Indonesia", music_genres=None):
    # Output language follows the selected target country. Indonesia is Indonesian by design.
    en = language == "English"
    ms = language == "Bahasa Melayu"
    ja = language == "Japanese"
    de = language == "German"

    if mode == "🎵 Music":
        genre_line = selected_music_genre_text(music_genres) or "selected music genre"
        if en:
            return f"""[INTRO / AUDIO HOOK 0:00–0:05]\n{title.upper()}!\n\n[VERSE 1]\nAbout {keyword}, shaped by {genre_line}, about the days we are living,\nsome things remain unsaid, some stories unfinished.\n\n[PRE-CHORUS]\nWhen the world keeps pushing us down,\nwe still have a reason to keep moving.\n\n[CHORUS]\n{title.upper()}\nWe fall, we rise again,\neven when it hurts, we are still here.\n\n[VERSE 2]\nReality arrives without warning,\nbut our story is not over.\n\n[BRIDGE]\nTake a breath. Look ahead.\nWe still have a voice.\n\n[FINAL CHORUS]\n{title.upper()}\nIt is not over — keep going!\n\n[OUTRO]\n{keyword}..."""
        if ms:
            return f"""[INTRO / AUDIO HOOK 0:00–0:05]\n{title.upper()}!\n\n[VERSE 1]\nTentang {keyword}, dibalut {genre_line}, tentang hari yang kita lalui,\nada yang tertahan, ada cerita yang belum selesai.\n\n[PRE-CHORUS]\nBiar dunia terus menekan,\nkita masih ada sebab untuk melangkah.\n\n[CHORUS]\n{title.upper()}\nKita jatuh, kita bangkit lagi,\nwalau berat, kita masih di sini.\n\n[VERSE 2]\nRealiti datang tanpa amaran,\ntapi cerita kita belum berakhir.\n\n[BRIDGE]\nTarik nafas. Pandang ke depan.\nKita masih punya suara.\n\n[FINAL CHORUS]\n{title.upper()}\nBelum selesai — teruskan melangkah!\n\n[OUTRO]\n{keyword}..."""
        # For Japanese/German and any unsupported language, keep a clean structural prompt rather than falsely claiming a translation.
        if ja:
            return f"""[INTRO]\n{title}\n\n[VERSE 1]\nテーマ: {keyword}\n\n[PRE-CHORUS]\n感情を高め、主人公の葛藤を描く。\n\n[CHORUS]\n{title}\n強いフックと印象的なメロディ。\n\n[VERSE 2]\n物語を前進させる。\n\n[BRIDGE]\n感情のピーク。\n\n[FINAL CHORUS]\n{title}\n\n[OUTRO]\n余韻を残して終える。"""
        if de:
            return f"""[INTRO]\n{title}\n\n[STROPHE 1]\nThema: {keyword}\n\n[PRE-CHORUS]\nDie Spannung und Emotion steigern.\n\n[CHORUS]\n{title}\nStarker Hook und einprägsame Melodie.\n\n[STROPHE 2]\nDie Geschichte weiterführen.\n\n[BRIDGE]\nEmotionaler Höhepunkt.\n\n[FINAL CHORUS]\n{title}\n\n[OUTRO]\nMit einem bleibenden Gefühl enden."""
        return f"""[INTRO / AUDIO HOOK 0:00–0:05]\n{title.upper()}!\n\n[VERSE 1]\nTentang {keyword}, tentang hari yang kita jalani,\nada yang tertahan, ada yang belum selesai.\n\n[PRE-CHORUS]\nKalau dunia terus menekan,\nkita tetap punya alasan untuk berjalan.\n\n[CHORUS]\n{title.upper()}\nKita jatuh, kita bangkit lagi,\nmeski berat, kita tetap di sini.\n\n[VERSE 2]\nRealita datang tanpa aba-aba,\ntapi cerita kita belum selesai.\n\n[BRIDGE]\nTarik napas. Lihat ke depan.\nKita masih punya suara.\n\n[FINAL CHORUS]\n{title.upper()}\nBelum selesai — GAS LAGI!\n\n[OUTRO]\n{keyword}..."""

    # Non-music modes already use format-specific scripts; localize the generic framing where practical.
    if mode == "🧒 Cerita Anak":
        if en: return f"""[OPENING]\nOne day, {keyword} experienced something very strange...\n\n[SETUP]\nThe main character discovers a problem they have never seen before.\n\n[ADVENTURE]\nThe journey begins with obstacles, new friends, and a secret.\n\n[LESSON]\nCourage means trying even when you are afraid.\n\n[ENDING]\nThe problem is solved, but a new adventure is about to begin."""
        return f"""[OPENING]\nSuatu hari, {keyword} mengalami sesuatu yang sangat aneh...\n\n[SETUP]\nTokoh utama menemukan masalah yang belum pernah ia lihat sebelumnya.\n\n[ADVENTURE]\nPerjalanan dimulai. Ada rintangan, teman baru, dan satu rahasia.\n\n[LESSON]\nKeberanian berarti tetap mencoba walaupun takut.\n\n[ENDING]\nMasalah selesai, tetapi petualangan baru saja dimulai."""
    if mode == "🌍 Berita Dunia":
        return f"""[HOOK]\nWhat is really happening with {keyword}?\n\n[CONTEXT]\nExplain the event with date, location, and parties involved.\n\n[WHAT HAPPENED]\nBuild the chronology from verifiable sources.\n\n[WHY IT MATTERS]\nExplain the impact on people, economy, security, or policy.\n\n[WHAT NEXT]\nExplain the next developments and what remains unknown.\n\n[DISCLAIMER]\nSeparate verified facts, statements, and analysis.""" if en else f"""[HOOK]\nApa yang sebenarnya terjadi dengan {keyword}?\n\n[CONTEXT]\nJelaskan kejadian utama dengan tanggal, lokasi, dan pihak yang terlibat.\n\n[WHAT HAPPENED]\nSusun kronologi berdasarkan sumber yang dapat diverifikasi.\n\n[WHY IT MATTERS]\nTerangkan dampak terhadap masyarakat, ekonomi, keamanan, atau kebijakan.\n\n[WHAT NEXT]\nJelaskan perkembangan berikutnya dan apa yang masih belum diketahui.\n\n[DISCLAIMER]\nBedakan fakta, pernyataan pihak terkait, dan analisis."""
    if mode == "👻 Horror":
        return f"""[HOOK]\nDon't turn off the lights before the story of {keyword} ends.\n\n[SETUP]\nThe main character discovers something that should not exist.\n\n[ESCALATION]\nA small detail becomes an increasingly disturbing pattern.\n\n[REVEAL]\nOne clue changes the meaning of everything.\n\n[ENDING]\nAnd after that night, nothing was ever quite the same.""" if en else f"""[HOOK]\nJangan matikan lampu sebelum cerita {keyword} selesai.\n\n[SETUP]\nTokoh utama menemukan sesuatu yang tidak seharusnya ada.\n\n[ESCALATION]\nHal kecil berubah menjadi pola yang semakin mengganggu.\n\n[REVEAL]\nSatu petunjuk mengubah seluruh arti kejadian.\n\n[ENDING]\nDan sejak malam itu, tidak ada yang benar-benar sama."""
    if mode == "🎮 Gaming":
        return f"""[HOOK]\nIf you still do this in {keyword}, stop for a second.\n\n[PROBLEM]\nThe most common player mistake.\n\n[SOLUTION]\nStep 1 — setup.\nStep 2 — timing.\nStep 3 — execution.\n\n[PAYOFF]\nShow the result before and after.\n\n[CTA]\nTry it yourself and compare the result.""" if en else f"""[HOOK]\nKalau kamu masih melakukan ini di {keyword}, berhenti dulu.\n\n[PROBLEM]\nKesalahan paling umum pemain.\n\n[SOLUTION]\nLangkah 1 — setup.\nLangkah 2 — timing.\nLangkah 3 — eksekusi.\n\n[PAYOFF]\nTunjukkan hasil sebelum dan sesudah.\n\n[CTA]\nCoba sendiri dan bandingkan hasilnya."""
    if mode == "📚 Education":
        return f"""[HOOK]\n{keyword} is not as complicated as you think.\n\n[CONCEPT]\nExplain one main concept in simple language.\n\n[EXAMPLE]\nGive a real-world example.\n\n[COMMON MISTAKE]\nShow a common mistake.\n\n[RECAP]\nSummarize the three key points.""" if en else f"""[HOOK]\n{keyword} sebenarnya tidak serumit yang kamu kira.\n\n[CONCEPT]\nJelaskan satu konsep utama dengan bahasa sederhana.\n\n[EXAMPLE]\nBerikan contoh kehidupan nyata.\n\n[COMMON MISTAKE]\nTunjukkan kesalahan yang sering terjadi.\n\n[RECAP]\nRangkum tiga poin utama dalam kalimat singkat."""
    if mode == "😂 Comedy":
        return f"""[SETUP]\nWe have all dealt with {keyword}.\n\n[EXPECTATION]\nEverything looks easy.\n\n[REALITY]\nThen life has other plans.\n\n[ESCALATION]\nA small problem becomes absurdly serious.\n\n[PUNCHLINE]\nIn the end, the problem was not {keyword}. We were just too confident.""" if en else f"""[SETUP]\nKita semua pernah menghadapi {keyword}.\n\n[EXPECTATION]\nSemua terlihat mudah.\n\n[REALITY]\nTernyata hidup punya rencana lain.\n\n[ESCALATION]\nMasalah kecil berubah menjadi masalah yang terlalu serius.\n\n[PUNCHLINE]\nAkhirnya kita sadar: ternyata masalahnya bukan {keyword}. Masalahnya kita terlalu percaya diri."""
    return f"""[HOOK]\nWhy does {keyword} matter?\n\n[CONTEXT]\nGive brief context.\n\n[MAIN POINT]\nExplain one key idea with a concrete example.\n\n[PAYOFF]\nGive a memorable different perspective.\n\n[ENDING]\nClose with a line that makes viewers want to know more.""" if en else f"""[HOOK]\nKenapa {keyword} penting untuk dibahas?\n\n[CONTEXT]\nBerikan konteks singkat.\n\n[MAIN POINT]\nJelaskan satu ide utama dengan contoh konkret.\n\n[PAYOFF]\nBerikan sudut pandang yang berbeda dan mudah diingat.\n\n[ENDING]\nTutup dengan satu kalimat yang membuat penonton ingin tahu lebih jauh."""


def style_prompt(mode, dna, keyword, language="Bahasa Indonesia", music_genres=None):
    if mode == "🎵 Music":
        gtxt = selected_music_genre_text(music_genres) or "Rock / Pop"
        return (f"{gtxt}. Target language: {language}. Emotional or characterful vocal, immediate audio hook, strong chorus, tight rhythm section, cinematic atmosphere, clear bass, memorable melody, no long intro, blend the selected genres coherently, original arrangement.")
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


def seo_package(mode, title, keyword, dna, country_name="Indonesia", music_genres=None):
    tags = [keyword, MODE_LIBRARY[mode]["niche"], "youtube", "shorts"]
    if mode == "🎵 Music":
        tags += (["musik indonesia", "lagu indonesia"] if country_name == "Indonesia" else ["music", "song"])
        tags += [x.lower().replace("— ", "").replace(" / ", " ") for x in (music_genres or [])]
    elif mode == "🧒 Cerita Anak":
        tags += (["cerita anak", "dongeng"] if country_name == "Indonesia" else ["kids story", "children stories"])
    elif mode == "🌍 Berita Dunia":
        tags += (["berita dunia", "berita terbaru"] if country_name == "Indonesia" else ["world news", "news update"])
    hashtags = " ".join("#" + re.sub(r"[^A-Za-z0-9]", "", x.title().replace(" ", "")) for x in tags[:6])
    description = f"{title}\n\nTopic: {keyword}\n\nCreative DNA: {dna}\nTarget: {country_name}\nLanguage: {LANGUAGE_LABELS.get(country_name, 'English')}\nFormat: {MODE_LIBRARY[mode]['formats']}\n\n{hashtags}"
    return description, hashtags

# =========================================================
# MUSIC / SUNO AUDIO ANALYZER
# =========================================================
def _fmt_time(seconds):
    seconds = int(max(0, seconds))
    return f"{seconds//60}:{seconds%60:02d}"


def _scale01(value, lo, hi):
    if hi <= lo:
        return 0.0
    return float(np.clip((value - lo) / (hi - lo), 0, 1))


def analyze_music_file(uploaded_file):
    """Lightweight signal analysis for MP3/WAV. Genre/instrument/vocal labels are estimates."""
    if librosa is None or np is None:
        raise RuntimeError(f"Audio analyzer belum tersedia: {AUDIO_IMPORT_ERROR}")
    suffix = os.path.splitext(uploaded_file.name)[1].lower() or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        path = tmp.name
    try:
        y, sr = librosa.load(path, sr=22050, mono=True)
        if len(y) < sr * 3:
            raise RuntimeError("Audio terlalu pendek. Gunakan file minimal sekitar 3 detik.")
        duration = len(y) / sr
        hop = 512
        rms = librosa.feature.rms(y=y, hop_length=hop)[0]
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop)[0]
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=hop)[0]
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, roll_percent=0.85, hop_length=hop)[0]
        zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop)[0]
        chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=hop)
        contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop)
        tempo_arr, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop)
        tempo = float(np.asarray(tempo_arr).reshape(-1)[0])
        tempo = max(40.0, min(220.0, tempo))

        # HPSS gives a useful but non-semantic harmonic/percussive balance.
        harmonic, percussive = librosa.effects.hpss(y)
        h_rms = float(np.sqrt(np.mean(harmonic**2)) + 1e-9)
        p_rms = float(np.sqrt(np.mean(percussive**2)) + 1e-9)
        hp_ratio = p_rms / (h_rms + p_rms)

        energy = float(np.mean(rms))
        energy_score = round(_scale01(energy, 0.02, 0.22) * 100)
        bright = float(np.median(centroid) / (sr / 2))
        low = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
        low_band = float(np.mean(librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=sr/2)[:12]))
        mid_band = float(np.mean(librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=sr/2)[12:36]))
        high_band = float(np.mean(librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=sr/2)[36:]))
        total_band = max(low_band + mid_band + high_band, 1e-9)
        low_pct, mid_pct, high_pct = [100*x/total_band for x in (low_band, mid_band, high_band)]

        # Mood: heuristic, intentionally presented as estimated rather than ground truth.
        if energy_score >= 70 and tempo >= 125:
            mood = "Energetic / Aggressive"
        elif energy_score >= 55 and tempo >= 105:
            mood = "Driving / Powerful"
        elif energy_score < 35 and tempo < 90:
            mood = "Calm / Melancholic"
        elif energy_score < 50:
            mood = "Emotional / Atmospheric"
        else:
            mood = "Balanced / Emotional"

        # Broad style family heuristic from tempo + energy + spectral balance.
        if tempo >= 145 and energy_score >= 65:
            genre = "Rock / Metal / High-energy"
        elif 95 <= tempo <= 125 and hp_ratio >= 0.48 and low_pct >= 34:
            genre = "Groove / Dangdut / Pop-Rock"
        elif tempo < 95 and energy_score < 50:
            genre = "Ballad / Lo-fi / Atmospheric"
        elif high_pct >= 34 and tempo >= 115:
            genre = "Electronic / Pop / Dance"
        else:
            genre = "Pop / Rock / Contemporary"

        # Production/instrumental character from spectral energy, not literal instrument detection.
        instrument = []
        if low_pct >= 38:
            instrument.append("strong low-end / kick-bass")
        if mid_pct >= 35:
            instrument.append("midrange-forward / guitar-vocal body")
        if high_pct >= 30:
            instrument.append("bright percussion / cymbal-synth presence")
        if hp_ratio >= 0.58:
            instrument.append("percussive arrangement")
        else:
            instrument.append("harmonic / sustained arrangement")

        vocal = "Vocal-like midrange presence (estimated)" if mid_pct >= 30 and h_rms > 0 else "Instrumental / vocal not reliably separable"
        if zcr.mean() > 0.11:
            vocal += " • brighter/raspier texture possible"
        else:
            vocal += " • smoother/darker texture possible"

        # Key estimate: chroma peak. This is approximate and can be wrong for modal/mixed music.
        chroma_mean = chroma.mean(axis=1)
        key_names = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        key_est = key_names[int(np.argmax(chroma_mean))]
        major_profile = np.array([1,0,0,0,1,0,0,1,0,1,0,0], dtype=float)
        # Only call it a root estimate; do not claim major/minor certainty.
        key_conf = float(np.max(chroma_mean) / (np.mean(chroma_mean)+1e-9))

        # Song sections / structure proxy using RMS changes.
        rms_smooth = np.convolve(rms, np.ones(21)/21, mode='same')
        change = np.abs(np.diff(rms_smooth, prepend=rms_smooth[0]))
        peaks = np.argsort(change)[-12:]
        section_points = sorted(set([0] + [int(p * hop / sr) for p in peaks if p*hop/sr < duration-2] + [int(duration)]))
        section_points = section_points[:10]

        result = {
            "filename": uploaded_file.name,
            "duration": duration,
            "tempo": tempo,
            "energy": energy_score,
            "genre": genre,
            "mood": mood,
            "key": f"{key_est} (root estimate)",
            "key_confidence": round(min(key_conf/4, 1)*100),
            "instrument_profile": instrument,
            "vocal_profile": vocal,
            "low_pct": round(low_pct, 1),
            "mid_pct": round(mid_pct, 1),
            "high_pct": round(high_pct, 1),
            "percussive_pct": round(hp_ratio*100, 1),
            "spectral_centroid": round(float(np.median(centroid))),
            "spectral_bandwidth": round(float(np.median(bandwidth))),
            "rolloff": round(float(np.median(rolloff))),
            "zcr": round(float(np.mean(zcr)), 4),
            "sections": section_points,
        }
        result["suno_style"] = build_suno_style_from_analysis(result)
        result["suno_tags"] = build_suno_tags(result)
        result["suno_structure"] = build_suno_structure(result)
        return result
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def build_suno_style_from_analysis(a):
    return (
        f"{a['genre']}, {a['mood']}, {a['tempo']:.0f} BPM, {a['vocal_profile']}, "
        f"{', '.join(a['instrument_profile'][:3])}, cinematic production, clear low end, "
        "dynamic chorus, memorable melody, controlled intro, original arrangement"
    )


def build_suno_tags(a):
    tags = ["[Intro]"]
    if a["energy"] >= 65:
        tags += ["[Verse]", "[Pre-Chorus]", "[Chorus]", "[Drop / Instrumental Break]", "[Bridge]", "[Final Chorus]", "[Outro]"]
    else:
        tags += ["[Verse 1]", "[Pre-Chorus]", "[Chorus]", "[Verse 2]", "[Bridge]", "[Final Chorus]", "[Outro]"]
    return " ".join(tags)


def build_suno_structure(a):
    return f"""[Intro]
Atmospheric opening, establish {a['mood'].lower()} mood.

[Verse 1]
Introduce the story and emotional point of view.

[Pre-Chorus]
Increase tension and melodic lift.

[Chorus]
Big memorable hook; strongest emotional payoff.

[Verse 2]
Develop the story with new details.

[Bridge]
Contrast section; strip back or change texture.

[Final Chorus]
Full energy and strongest vocal delivery.

[Outro]
Resolve naturally and leave a memorable final phrase."""

# =========================================================
# SESSION STATE
# =========================================================
for key, default in {
    "research_result": None,
    "active_keyword": "",
    "selected_title": "",
    "script": "",
    "script_editor": "",
    "music_analysis": None,
    "music_genres": [],
    "angles": [],
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
    if mode == "🎵 Music":
        music_genres = st.multiselect(
            "🎼 Pilih Genre Musik (boleh banyak)",
            list(MUSIC_GENRE_GROUPS.keys()),
            default=st.session_state.get("music_genres", []),
            help="Contoh: pilih A + B + D. Factory akan mencampurkan ketiga DNA genre tersebut ke keyword, style, title, lyric, artwork, dan SEO."
        )
        st.session_state.music_genres = music_genres
    else:
        music_genres = []
        st.session_state.music_genres = []
    if st.button("🤖 AUTO MODE DARI DNA", use_container_width=True):
        mode = infer_mode(dna)
        st.session_state.auto_mode = mode
        st.rerun()
    country_name = st.selectbox("🎯 Target Country", list(COUNTRIES.keys()), index=0)
    st.caption(f"Mode terdeteksi: **{mode_auto}**")
    st.caption("DNA menentukan arah kreatif. Niche, keyword, format, dan output mengikuti mode.")

# Reset downstream selections whenever the creative context changes. This prevents an old Music keyword/title from leaking into a new niche.
_context_sig = f"{dna.strip()}||{mode}||{country_name}||{"|".join(music_genres)}"
if st.session_state.get("context_signature") != _context_sig:
    st.session_state.context_signature = _context_sig
    st.session_state.active_keyword = ""
    st.session_state.selected_title = ""
    st.session_state.title_pool = []
    st.session_state.research_result = None
    st.session_state.script = ""
    st.session_state.script_editor = ""

# =========================================================
# TABS
# =========================================================
tabs = st.tabs([
    "🌍 RESEARCH + AUTO KEYWORD",
    "💡 CONTENT IDEAS",
    "🎯 TITLE LAB",
    "🎧 MUSIC / SUNO ANALYZER",
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
        genre_line = f"\n\n**Genre dipilih:** {selected_music_genre_text(music_genres)}" if mode == "🎵 Music" and music_genres else ""
        st.info(f"**DNA:** {dna}\n\n**Mode:** {mode}{genre_line}\n\n**Target:** {country_name}")
    with c2:
        if st.button("🔥 CARI KEYWORD OTOMATIS", use_container_width=True, type="primary"):
            with st.spinner("Mencari sinyal keyword + riset YouTube..."):
                try:
                    result = run_auto_research(dna, mode, country_name, custom_keyword, max_per_keyword, music_genres)
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
    if result:
        st.subheader("📊 Cara Membaca Hasil Keyword")
        st.markdown(
            "**Signal** = seberapa kuat pola keyword muncul di hasil riset + performa video yang memuatnya. "
            "**Evidence** = jumlah video yang mendukung keyword. "
            "**Avg Opportunity** = rata-rata opportunity video pendukung. "
            "Jangan memilih keyword hanya karena Signal tertinggi: cari kombinasi **Signal tinggi + Evidence cukup + Opportunity bagus + sesuai DNA**."
        )
        kw_rows = result.get("keyword_candidates", [])
        if kw_rows:
            # compact decision table
            kw_df = pd.DataFrame(kw_rows)
            show_cols = [c for c in ["Keyword", "Signal", "Evidence", "Avg Opportunity", "Views Evidence", "Views/Day Evidence"] if c in kw_df.columns]
            st.dataframe(kw_df[show_cols].head(15), use_container_width=True, hide_index=True)

            st.subheader("🏆 Rekomendasi Keyword")
            ranked = sorted(kw_rows, key=lambda x: (safe_num(x.get("Signal")), safe_num(x.get("Avg Opportunity"))), reverse=True)
            for i, row in enumerate(ranked[:5], 1):
                evidence = int(row.get("Evidence", 0))
                opp = safe_num(row.get("Avg Opportunity"))
                signal = safe_num(row.get("Signal"))
                verdict = "KUAT" if signal >= 500 and evidence >= 3 and opp >= 50 else "MENARIK" if signal >= 250 and evidence >= 2 else "UJI DULU"
                st.markdown(f"**{i}. {row['Keyword']} — {verdict}**  \nSignal **{signal:.1f}** · Evidence **{evidence} video** · Avg Opportunity **{opp:.1f}**")

        st.subheader("💡 Content Ideas dari Keyword Terpilih")
        st.caption("Idea di bawah bukan judul final. Ini adalah angle/topik yang bisa dikembangkan menjadi video. Pilih angle yang paling cocok dengan DNA dan audience.")
        ideas = []
        # Build ideas from the strongest keyword signals instead of blindly displaying generic research-engine ideas.
        source_keywords = [x.get("Keyword", "") for x in sorted(kw_rows, key=lambda x: (safe_num(x.get("Signal")), safe_num(x.get("Avg Opportunity"))), reverse=True)[:5]]
        source_keywords = [x for x in source_keywords if x]
        for kw in source_keywords[:5]:
            if mode == "🎵 Music":
                ideas.extend([
                    f"{kw}: cerita/emosi yang paling relatable bagi audience",
                    f"{kw}: konflik atau realita yang jarang dibahas",
                    f"{kw}: versi {selected_music_genre_text(music_genres) or 'genre pilihan'} dengan sudut pandang original",
                ])
            elif mode == "🧒 Cerita Anak":
                ideas.extend([f"Petualangan karakter menghadapi {kw}", f"Pelajaran/moral dari {kw}", f"Misteri kecil di sekitar {kw}"])
            elif mode == "🌍 Berita Dunia":
                ideas.extend([f"{kw}: apa yang terjadi", f"{kw}: kronologi dan dampaknya", f"{kw}: apa artinya bagi audience"])
            elif mode == "👻 Horror":
                ideas.extend([f"Kisah misteri yang berawal dari {kw}", f"{kw}: kejadian paling aneh", f"{kw}: versi cerita dari sudut pandang saksi"])
            elif mode == "🎮 Gaming":
                ideas.extend([f"{kw}: tips yang jarang diketahui", f"{kw}: kesalahan pemain", f"{kw}: challenge/experiment original"])
            elif mode == "📚 Education":
                ideas.extend([f"{kw} dijelaskan dari nol", f"3 kesalahan umum tentang {kw}", f"{kw}: contoh paling mudah dipahami"])
            elif mode == "😂 Comedy":
                ideas.extend([f"Ekspektasi vs realita: {kw}", f"POV: menghadapi {kw}", f"Kalau {kw} jadi masalah sehari-hari"])
            else:
                ideas.extend([f"Realita di balik {kw}", f"Sudut pandang berbeda tentang {kw}", f"Apa yang jarang dibahas dari {kw}?"])
        # de-duplicate while preserving order
        seen = set()
        ideas = [x for x in ideas if not (x in seen or seen.add(x))]
        for i, idea in enumerate(ideas[:15], 1):
            st.markdown(f"**{i:02d}.** {idea}")
    else:
        st.info("Lakukan riset dulu. Setelah keyword muncul, gunakan tabel di atas untuk menilai Signal, Evidence, dan Opportunity sebelum memilih Content Idea.")

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
            f"Pelajaran berikutnya dari {active_kw}",
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
    title_pool = title_candidates(mode, active_kw, dna, music_genres)
    if st.button("🚀 GENERATE PILIHAN JUDUL", use_container_width=True):
        st.session_state.title_pool = title_pool
    for i, title in enumerate(st.session_state.get("title_pool", title_pool), 1):
        st.markdown(f"**{i}. {title}**")
        if st.button(f"✅ PILIH #{i}", key=f"pick_title_{i}"):
            st.session_state.selected_title = title
            st.success(f"Judul aktif: **{title}**")
    st.caption("Judul dibuat berdasarkan mode + keyword aktif. Opportunity research membantu arah topik, bukan jaminan viral.")

# =========================================================
# MUSIC / SUNO ANALYZER
# =========================================================
with tabs[3]:
    st.header("🎧 Music / Suno Analyzer")
    st.write("Upload MP3/WAV untuk membaca karakter audio secara otomatis. Genre, mood, key, instrumen, dan vokal di bawah adalah **estimasi sinyal audio**, bukan identifikasi studio-level.")
    audio_file = st.file_uploader("🎵 Upload MP3 / WAV", type=["mp3", "wav", "m4a", "flac"], key="music_analyzer_upload")
    if librosa is None:
        st.error(f"Library audio belum terpasang: {AUDIO_IMPORT_ERROR}")
        st.info("Tambahkan `librosa` ke requirements.txt lalu restart Streamlit.")
    elif audio_file:
        st.audio(audio_file)
        if st.button("🔬 ANALYZE MUSIC", type="primary", use_container_width=True):
            with st.spinner("Menganalisis tempo, energi, spektrum, harmonic/percussive balance..."):
                try:
                    st.session_state.music_analysis = analyze_music_file(audio_file)
                    st.success("Analysis Complete")
                except Exception as e:
                    st.error(f"Analisis audio gagal: {e}")

    a = st.session_state.get("music_analysis")
    if a:
        st.divider()
        st.subheader("🎼 SONIC PROFILE")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Genre", a["genre"])
        m2.metric("Mood", a["mood"])
        m3.metric("Tempo", f"{a['tempo']:.0f} BPM")
        m4.metric("Energy", f"{a['energy']}/100")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🎹 AUDIO CHARACTER")
            st.write(f"**Duration:** {_fmt_time(a['duration'])}")
            st.write(f"**Key/root estimate:** {a['key']}")
            st.write(f"**Key confidence:** {a['key_confidence']}% (heuristic)")
            st.write(f"**Low / Mid / High:** {a['low_pct']}% / {a['mid_pct']}% / {a['high_pct']}%")
            st.write(f"**Percussive vs harmonic:** {a['percussive_pct']}% percussive")
        with c2:
            st.markdown("### 🥁 INSTRUMENT / VOCAL PROFILE")
            for x in a["instrument_profile"]:
                st.write(f"• {x}")
            st.write(f"• {a['vocal_profile']}")

        st.subheader("🏷️ SUNO META-TAGS READY")
        st.code(a["suno_tags"])

        st.subheader("🎚️ SUNO STYLE READY")
        st.code(a["suno_style"])

        st.subheader("✍️ SUNO SONG STRUCTURE")
        st.code(a["suno_structure"])

        st.caption("Catatan: analisis audio ini sengaja ringan agar Streamlit Cloud tidak perlu model AI besar. Label genre/instrumen/vokal adalah inferensi dari tempo, energi, spektrum, dan harmonic/percussive balance; bukan transkripsi atau klasifikasi musik profesional.")

# =========================================================
# SCRIPT / LYRIC
# =========================================================
with tabs[4]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna, music_genres)[0]
    st.header(f"✍️ {MODE_LIBRARY[mode]['script_name']} Lab")
    title_from_input = st.text_input("Judul aktif", value=active_title, key="script_title_input")
    if st.button("🎬 GENERATE SCRIPT / LYRIC", use_container_width=True):
        generated = make_script(mode, title_from_input, active_kw, dna, LANGUAGE_LABELS.get(country_name, "Bahasa Indonesia"), music_genres)
        st.session_state.script = generated
        st.session_state.script_editor = generated
    st.text_area("Output editable", height=500, key="script_editor")
    st.session_state.script = st.session_state.get("script_editor", "")

# =========================================================
# STYLE + ARTWORK
# =========================================================
with tabs[5]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna, music_genres)[0]
    st.header("🎨 Style + Artwork Lab")
    st.subheader("Style / Production Prompt")
    st.code(style_prompt(mode, dna, active_kw, LANGUAGE_LABELS.get(country_name, "Bahasa Indonesia"), music_genres))
    st.subheader("🖼️ 5 Artwork / Visual Concepts")
    for name, prompt in artwork_prompts(mode, active_title, active_kw, dna):
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.code(prompt)
            st.caption("Gunakan konsep yang paling cocok dengan audience dan packaging channel.")

# =========================================================
# SEO
# =========================================================
with tabs[6]:
    active_kw = st.session_state.get("active_keyword", "") or topic_from_dna(dna, mode)
    active_title = st.session_state.get("selected_title", "") or title_candidates(mode, active_kw, dna, music_genres)[0]
    st.header("🚀 YouTube SEO")
    description, hashtags = seo_package(mode, active_title, active_kw, dna, country_name, music_genres)
    st.text_input("YouTube Title", value=active_title, key="seo_title")
    st.text_area("Description", value=description, height=260, key="seo_description")
    st.text_input("Hashtags", value=hashtags, key="seo_hashtags")
    st.caption("SEO helper berfokus pada kejelasan topik dan packaging. Research signal bukan jaminan ranking.")

st.divider()
st.caption("3D GOKIL AI CONTENT FACTORY • Universal DNA Engine • Audience/Trend Research • Auto Keyword Finder")
