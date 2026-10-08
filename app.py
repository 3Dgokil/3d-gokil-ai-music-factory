import os
import re
import math
import tempfile
from collections import defaultdict

import pandas as pd
import streamlit as st

# =========================================================
# OPTIONAL AUDIO ANALYZER
# =========================================================
try:
    import librosa
    import numpy as np
    AUDIO_IMPORT_ERROR = None
except Exception as e:
    librosa = None
    np = None
    AUDIO_IMPORT_ERROR = str(e)

st.set_page_config(page_title="3D GOKIL Music Content Factory", page_icon="🎵", layout="wide")

# =========================================================
# YOUTUBE RESEARCH
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
# CORE CONFIG
# =========================================================
DEFAULT_DNA = "CINTA — hubungan, kehilangan, kerinduan, penyesalan, dan emosi manusia."

COUNTRIES = {
    "🇺🇸 United States": ("US", "en", "English"),
    "🇮🇩 Indonesia": ("ID", "id", "Bahasa Indonesia"),
    "🇬🇧 United Kingdom": ("GB", "en", "English"),
    "🇦🇺 Australia": ("AU", "en", "English"),
    "🇨🇦 Canada": ("CA", "en", "English"),
    "🇩🇪 Germany": ("DE", "de", "German"),
    "🇯🇵 Japan": ("JP", "ja", "Japanese"),
    "🇲🇾 Malaysia": ("MY", "ms", "Bahasa Melayu"),
    "🌍 Global": (None, "en", "English"),
}

GENRE_GROUPS = {
    "A — ROCK / METAL": ["Rock", "Hard Rock", "Heavy Metal", "Alternative Rock"],
    "B — DANGDUT / KOPLO": ["Dangdut", "Koplo", "Modern Dangdut", "Rock Dangdut"],
    "C — ELECTRONIC / CYBER": ["Electronic", "EDM", "Synthwave", "Cyberpunk"],
    "D — NUSANTARA / TRADITIONAL": ["Gamelan", "Suling Jawa", "Ethnic Fusion", "Indonesian Folk"],
    "E — POP / ALTERNATIVE": ["Pop", "Indie Pop", "Alternative", "Lo-fi"],
}

GENRE_SEARCHES = {
    "A — ROCK / METAL": ["rock music", "heavy metal music", "hard rock music", "alternative rock music"],
    "B — DANGDUT / KOPLO": ["dangdut music", "koplo music", "modern dangdut", "rock dangdut"],
    "C — ELECTRONIC / CYBER": ["electronic music", "EDM music", "synthwave music", "cyberpunk music"],
    "D — NUSANTARA / TRADITIONAL": ["gamelan music", "Javanese gamelan", "suling jawa", "Indonesian ethnic music"],
    "E — POP / ALTERNATIVE": ["pop music", "indie pop music", "alternative music", "lofi music"],
}

THEME_PACKS = {
    "English": [
        ("❤️ Love & Relationships", ["love songs", "relationship songs", "heartbreak songs"]),
        ("👨‍👩‍👧 Parents & Family", ["songs about parents", "songs about mother and father", "family songs"]),
        ("💸 Money / Cost of Living", ["cost of living songs", "money problems songs", "financial struggle songs"]),
        ("🌎 Society / Country Conditions", ["social issues songs", "songs about society", "songs about the country"]),
        ("💼 Work / Life Pressure", ["work stress songs", "working life songs", "life struggle songs"]),
        ("🧠 Mental / Inner Struggle", ["mental struggle songs", "loneliness songs", "anxiety songs"]),
    ],
    "Bahasa Indonesia": [
        ("❤️ Cinta & Hubungan", ["lagu cinta", "lagu patah hati", "lagu hubungan"]),
        ("👨‍👩‍👧 Orang Tua & Keluarga", ["lagu tentang orang tua", "lagu ibu ayah", "lagu keluarga"]),
        ("💸 Uang / Keadaan Ekonomi", ["lagu masalah ekonomi", "lagu tanggal tua", "lagu biaya hidup"]),
        ("🌎 Keadaan Negara / Sosial", ["lagu masalah sosial", "lagu keadaan Indonesia", "lagu kritik sosial"]),
        ("💼 Kerja / Beban Hidup", ["lagu kehidupan kerja", "lagu tekanan hidup", "lagu pekerja"]),
        ("🧠 Pergulatan Batin", ["lagu kesepian", "lagu perjuangan hidup", "lagu keresahan"]),
    ],
    "Bahasa Melayu": [
        ("❤️ Cinta & Hubungan", ["lagu cinta", "lagu patah hati", "lagu hubungan"]),
        ("👨‍👩‍👧 Ibu Bapa & Keluarga", ["lagu tentang ibu bapa", "lagu keluarga", "lagu ibu ayah"]),
        ("💸 Duit / Kos Sara Hidup", ["lagu masalah kewangan", "kos sara hidup lagu", "lagu susah hidup"]),
        ("🌎 Masyarakat / Negara", ["lagu masalah sosial", "lagu masyarakat", "lagu tentang negara"]),
        ("💼 Kerja / Tekanan Hidup", ["lagu tekanan kerja", "lagu kehidupan", "lagu pekerja"]),
    ],
    "German": [
        ("❤️ Liebe & Beziehungen", ["Liebeslieder", "Trennung Lieder", "Beziehung Songs"]),
        ("👨‍👩‍👧 Eltern & Familie", ["Lieder über Eltern", "Mutter Vater Lied", "Familienlieder"]),
        ("💸 Geld / Lebenshaltungskosten", ["Lebenshaltungskosten Lied", "Geldprobleme Songs", "finanzielle Sorgen Lied"]),
        ("🌎 Gesellschaft / Land", ["soziale Probleme Songs", "Gesellschaft Lied", "Deutschland Song Gesellschaft"]),
        ("💼 Arbeit / Lebensdruck", ["Arbeitsstress Lied", "Arbeitsleben Songs", "Lebensdruck Lied"]),
    ],
    "Japanese": [
        ("❤️ 恋愛・失恋", ["恋愛ソング", "失恋ソング", "恋愛 歌"]),
        ("👨‍👩‍👧 親・家族", ["親への歌", "母 父 歌", "家族の歌"]),
        ("💸 お金・生活苦", ["生活苦 歌", "お金の悩み 歌", "物価高 歌"]),
        ("🌎 社会・国の現状", ["社会問題 歌", "日本 社会 歌", "社会風刺 歌"]),
        ("💼 仕事・人生のプレッシャー", ["仕事 ストレス 歌", "働く人生 歌", "人生 苦労 歌"]),
    ],
}

LANG_HINTS = {
    "English": "Write the final song in natural English.",
    "Bahasa Indonesia": "Tulis lagu dalam Bahasa Indonesia yang natural.",
    "German": "Schreibe den Song in natürlichem Deutsch.",
    "Japanese": "自然な日本語で歌詞を書く。",
    "Bahasa Melayu": "Tulis lagu dalam Bahasa Melayu yang natural.",
}

STYLE_VARIANTS = [
    ("01 — EMOTIONAL", "emosional, vulnerable, intimate, strong melodic chorus"),
    ("02 — DARK", "dark, tense, haunting, dramatic, heavier emotional contrast"),
    ("03 — POWERFUL", "powerful, aggressive, anthemic, explosive chorus"),
    ("04 — SEMI-FUNNY", "serious core with subtle intelligent humor, not parody"),
    ("05 — CINEMATIC", "cinematic, atmospheric, visual storytelling, emotional climax"),
]

ART_VARIANTS = [
    ("01 — SERIUS", "serious cinematic 3D, emotionally grounded, premium realistic character"),
    ("02 — CINEMATIC", "epic cinematic 3D, dramatic lighting, strong depth and composition"),
    ("03 — SEMI-FUNNY", "serious character with a subtle absurd/funny visual detail, tasteful and intelligent"),
    ("04 — GOKIL", "bold dimensional 3D, unexpected but coherent visual metaphor, funny without becoming childish"),
    ("05 — DARK / MYSTICAL", "dark mystical cinematic 3D, restrained symbolism, atmospheric depth"),
]

# =========================================================
# SESSION STATE
# =========================================================
DEFAULT_STATE = {
    "genre_research": None,
    "theme_rank": None,
    "selected_themes": [],
    "selected_keyword": "",
    "genre_rank": None,
    "research_result": None,
    "keyword_table": None,
    "content_ideas": [],
    "selected_idea": "",
    "titles": [],
    "selected_title": "",
    "lyrics": [],
    "selected_lyric": "",
    "artworks": [],
    "music_analysis": None,
}
for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v

# =========================================================
# HELPERS
# =========================================================
def clean(s, n=300):
    return re.sub(r"\s+", " ", str(s or "")).strip()[:n]


def selected_genres(groups):
    out = []
    for g in groups or []:
        out += GENRE_GROUPS.get(g, [g])
    return list(dict.fromkeys(out))


def fmt_num(v):
    try: v = float(v)
    except Exception: v = 0
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M"
    if v >= 1_000: return f"{v/1_000:.1f}K"
    return f"{int(v):,}"


def score_rows(result):
    rows = []
    for r in result.get("videos", []) or []:
        rows.append({
            "Opportunity": int(r.get("score", 0)),
            "Trend": r.get("trend", "-"),
            "Title": r.get("title", "-"),
            "Channel": r.get("channel", "-"),
            "Views": int(r.get("views", 0)),
            "Subscribers": int(r.get("subs", 0)),
            "Views/Day": int(float(r.get("vpd", 0))),
            "Engagement %": round(float(r.get("eng", 0)), 2),
        })
    return rows


def research_queries(queries, country, language, max_per=12):
    if research is None:
        raise RuntimeError(f"research.py tidak bisa dimuat: {RESEARCH_IMPORT_ERROR}")
    if not os.environ.get("YOUTUBE_API_KEY"):
        raise RuntimeError("YOUTUBE_API_KEY belum terbaca di Streamlit Secrets.")
    return research.research(", ".join(queries), country=country, language=language, max_per_keyword=max_per)


def theme_research(country_name):
    """Discover which broad human themes show the strongest relative YouTube opportunity in the target country.
    This is an internal research signal, not official YouTube search volume.
    """
    region, language, _ = COUNTRIES[country_name]
    packs = THEME_PACKS.get(language, THEME_PACKS["English"])
    rows = []
    for theme, queries in packs:
        res = research_queries(queries, region, language, max_per=8)
        vids = res.get("videos", []) or []
        scores = [float(x.get("score", 0)) for x in vids]
        views = [float(x.get("views", 0)) for x in vids]
        vpd = [float(x.get("vpd", 0)) for x in vids]
        rows.append({
            "Theme": theme,
            "Avg Opportunity": round(sum(scores)/len(scores), 1) if scores else 0,
            "Top Opportunity": max(scores) if scores else 0,
            "Views Evidence": int(sum(views)),
            "Views/Day Evidence": int(sum(vpd)),
            "Evidence": len(vids),
            "Top Video": vids[0].get("title", "-") if vids else "-",
        })
    rows.sort(key=lambda x: (x["Avg Opportunity"], x["Top Opportunity"], x["Views/Day Evidence"]), reverse=True)
    return rows


def genre_research(country_name):
    region, language, _ = COUNTRIES[country_name]
    all_rows = []
    for group, queries in GENRE_SEARCHES.items():
        # Search only the country-relevant language/context. The score is an internal opportunity signal,
        # not official YouTube search volume.
        q = queries[:]
        if country_name not in ("🇺🇸 United States", "🇬🇧 United Kingdom", "🇦🇺 Australia", "🇨🇦 Canada", "🌍 Global"):
            if country_name == "🇮🇩 Indonesia":
                q += ["musik " + x.replace(" music", "") for x in queries[:2]]
        res = research_queries(q, region, language, max_per=8)
        vids = res.get("videos", []) or []
        scores = [float(x.get("score", 0)) for x in vids]
        views = [float(x.get("views", 0)) for x in vids]
        vpd = [float(x.get("vpd", 0)) for x in vids]
        all_rows.append({
            "Genre Group": group,
            "Avg Opportunity": round(sum(scores)/len(scores), 1) if scores else 0,
            "Top Opportunity": max(scores) if scores else 0,
            "Views Evidence": int(sum(views)),
            "Views/Day Evidence": int(sum(vpd)),
            "Evidence": len(vids),
            "Top Video": vids[0].get("title", "-") if vids else "-",
        })
    all_rows.sort(key=lambda x: (x["Avg Opportunity"], x["Top Opportunity"], x["Views/Day Evidence"]), reverse=True)
    return all_rows


def keyword_candidates(result, allowed_genres, language):
    rows = result.get("videos", []) or []
    genre_words = set()
    for g in allowed_genres:
        genre_words.update(re.findall(r"[\w-]+", g.lower()))
    stop = {"the","and","for","with","this","that","from","official","video","full","live","best","new","music","song","lagu","musik","yang","dan","untuk","dengan","dari","ini","itu","2024","2025","2026","2027"}
    stats = defaultdict(lambda: {"signal":0.0,"evidence":0,"views":0,"vpd":0.0,"opp":0.0,"examples":[]})
    for r in rows:
        title = r.get("title", "")
        words = [w for w in re.findall(r"[\w-]+", title.lower()) if len(w) >= 3 and w not in stop]
        base = max(float(r.get("score",0)), 1)
        for i, w in enumerate(words):
            d = stats[w]
            boost = 1.5 if w in genre_words else 1.0
            d["signal"] += base * boost
            d["evidence"] += 1
            d["views"] += int(r.get("views",0))
            d["vpd"] += float(r.get("vpd",0))
            d["opp"] += base
            if len(d["examples"]) < 2: d["examples"].append(title)
        for a,b in zip(words, words[1:]):
            phrase = f"{a} {b}"
            d = stats[phrase]
            d["signal"] += base * (1.25 if a in genre_words or b in genre_words else 1.0)
            d["evidence"] += 1
            d["views"] += int(r.get("views",0))
            d["vpd"] += float(r.get("vpd",0))
            d["opp"] += base
            if len(d["examples"]) < 2: d["examples"].append(title)
    out=[]
    for kw,d in stats.items():
        if d["evidence"] < 2: continue
        out.append({
            "Keyword": kw,
            "Signal": round(d["signal"],1),
            "Evidence": d["evidence"],
            "Avg Opportunity": round(d["opp"]/d["evidence"],1),
            "Views Evidence": d["views"],
            "Views/Day Evidence": int(d["vpd"]),
            "Example": " | ".join(d["examples"]),
        })
    out.sort(key=lambda x:(x["Avg Opportunity"],x["Signal"],x["Evidence"]), reverse=True)
    return out[:20]


def make_content_ideas(keyword, dna, base_genre, accents, language):
    k = clean(keyword) or ("love" if language == "English" else "cinta")
    genre = ", ".join(base_genre if isinstance(base_genre,list) else [str(base_genre)])
    accent = ", ".join(accents) if accents else "none"
    if language == "English":
        core = [
            f"Someone loses the person they love because they realize their mistakes too late.",
            f"Two people still love each other, but life forces them to separate.",
            f"Someone looks strong outside while secretly waiting for an old love to return.",
            f"A relationship is collapsing into a battle between pride and love.",
            f"An old love returns after someone has finally tried to move on.",
        ]
    elif language == "Bahasa Melayu":
        core = [
            "Seseorang kehilangan orang yang dicintai kerana menyedari kesilapannya terlalu lewat.",
            "Dua orang masih saling mencintai tetapi hidup memaksa mereka berpisah.",
            "Seseorang kelihatan kuat di luar tetapi masih menunggu cinta lama kembali.",
            "Sebuah hubungan runtuh kerana pertarungan antara ego dan cinta.",
            "Cinta lama kembali ketika seseorang sudah cuba untuk move on.",
        ]
    elif language == "German":
        core = [
            "Jemand verliert die geliebte Person, weil er seine Fehler zu spät erkennt.",
            "Zwei Menschen lieben sich noch, doch das Leben zwingt sie zur Trennung.",
            "Jemand wirkt nach außen stark, wartet aber heimlich noch auf eine alte Liebe.",
            "Eine Beziehung zerbricht im Kampf zwischen Stolz und Liebe.",
            "Eine alte Liebe kehrt zurück, nachdem jemand versucht hat loszulassen.",
        ]
    elif language == "Japanese":
        core = [
            "愛する人を失い、遅すぎた後悔に気づく物語。",
            "まだ愛し合っている二人を、人生が引き離してしまう物語。",
            "強く見える人が、心の中で昔の恋を待ち続ける物語。",
            "プライドと愛の間で壊れていく関係の物語。",
            "前に進もうとした時、昔の恋が戻ってくる物語。",
        ]
    else:
        core = [
            "Seseorang kehilangan orang yang paling dicintainya karena kesalahan yang terlambat disadari.",
            "Dua orang masih saling mencintai tetapi hidup memaksa mereka berpisah.",
            "Seseorang terlihat kuat di luar, tetapi diam-diam masih menunggu cinta lama.",
            "Hubungan yang hampir hancur berubah menjadi pertarungan antara ego dan cinta.",
            "Cinta lama kembali ketika seseorang sudah mencoba move on.",
        ]
    return [f"{x} | Genre: {genre} | Accent: {accent}" for x in core]


def title_translation(title):
    t = title
    replacements = [
        ("I Was Too Late", "Aku Terlambat"),
        ("The Love I Couldn't Save", "Cinta yang Tak Bisa Kuselematkan"),
        ("You Left, I Stayed", "Kau Pergi, Aku Tinggal"),
        ("I Became a Stranger to You", "Aku Menjadi Orang Asing Bagimu"),
        ("One Last Night", "Malam Terakhir"),
    ]
    for a,b in replacements:
        if a in t:
            prefix=t.split(" — ")[0]
            return f"{prefix} — {b}"
    return t


def make_titles(idea, keyword, language, base_genre):
    k = clean(keyword) or "Love"
    # Titles are intentionally generated in the target language.
    if language == "English":
        return [
            f"{k.title()} — I Was Too Late",
            f"{k.title()} — The Love I Couldn't Save",
            f"{k.title()} — You Left, I Stayed",
            f"{k.title()} — I Became a Stranger to You",
            f"{k.title()} — One Last Night",
        ]
    if language == "Bahasa Melayu":
        return [
            f"{k.title()} — Aku Terlambat",
            f"{k.title()} — Cinta Yang Tak Dapat Diselamatkan",
            f"{k.title()} — Kau Pergi, Aku Tinggal",
            f"{k.title()} — Kita Jadi Asing",
            f"{k.title()} — Malam Terakhir",
        ]
    if language == "German":
        return [
            f"{k.title()} — Ich War Zu Spät",
            f"{k.title()} — Die Liebe, Die Ich Nicht Retten Konnte",
            f"{k.title()} — Du Gingst, Ich Blieb",
            f"{k.title()} — Fremd Geworden",
            f"{k.title()} — Eine Letzte Nacht",
        ]
    if language == "Japanese":
        return [
            f"{k} — 遅すぎた愛",
            f"{k} — 救えなかった恋",
            f"{k} — 君は去り、僕は残った",
            f"{k} — もう他人になった",
            f"{k} — 最後の夜",
        ]
    return [
        f"{k.upper()} — AKU TERLAMBAT",
        f"{k.upper()} — CINTA YANG TAK BISA KUSELAMATKAN",
        f"{k.upper()} — KAU PERGI, AKU TINGGAL",
        f"{k.upper()} — KITA JADI ASING",
        f"{k.upper()} — MALAM TERAKHIR",
    ]


def lyric_from_idea(title, idea, variant, language, genres, accents):
    tone = dict(STYLE_VARIANTS)[variant]
    genre_text = ", ".join(genres)
    accent_text = ", ".join(accents) if accents else "none"
    if language == "English":
        return f"""[TITLE] {title}\n[STYLE] {tone}\n[GENRE FUSION] {genre_text} + {accent_text}\n\n[INTRO]\nA short musical hook that immediately establishes the emotional conflict.\n\n[VERSE 1]\nI thought we had forever,\nbut forever slipped away.\nI kept the words inside my chest,\nuntil silence had its say.\n\n[PRE-CHORUS]\nNow every road leads back to you,\nevery memory cuts through.\n\n[CHORUS]\n{title}\nI was too late to save our love,\ntoo proud to see what we became.\nIf I could turn the night around,\nI'd call your name without the shame.\n\n[VERSE 2]\nThe room still holds your shadow,\nmy hands still know your shape.\nI learned that losing someone\nis not the same as being brave.\n\n[BRIDGE]\nIf this is where the story ends,\nlet the final note be true.\nI loved you more than I could say,\nand I still remember you.\n\n[FINAL CHORUS]\n{title}\nI was too late, but now I know,\nsome wounds become the songs we own.\n\n[OUTRO]\nA short emotional instrumental tail."""
    # Indonesian and other languages use a safe Indonesian fallback only when requested language is not implemented.
    if language == "Bahasa Indonesia":
        return f"""[JUDUL] {title}\n[NUANSA] {tone}\n[GENRE] {genre_text} + {accent_text}\n\n[INTRO]\nHook musik singkat yang langsung membuka konflik cinta.\n\n[VERSE 1]\nKupikir kita punya selamanya,\ntapi waktu membawa semuanya pergi.\nKata yang dulu tak sempat terucap,\nkini tinggal gema di dalam diri.\n\n[PRE-CHORUS]\nSetiap jalan kembali padamu,\nsetiap kenangan masih menusukku.\n\n[CHORUS]\n{title}\nAku terlambat menyelamatkan cinta,\nterlalu keras kepala melihat akhirnya.\nAndai malam bisa kuputar kembali,\nkan kupanggil namamu sekali lagi.\n\n[VERSE 2]\nRuangan ini masih menyimpan bayangmu,\ntanganku masih mengingatmu.\nKini aku tahu kehilangan seseorang\ntak selalu berarti kita sudah sembuh.\n\n[BRIDGE]\nJika ini akhir cerita kita,\nbiarkan nada terakhir berkata jujur.\n\n[FINAL CHORUS]\n{title}\nAku terlambat, tapi kini ku tahu,\nluka pun bisa berubah menjadi lagu.\n\n[OUTRO]\nBiarkan musik menyisakan kenangan."""
    return f"""[TITLE] {title}\n[STRUCTURE] Intro → Verse → Pre-Chorus → Chorus → Verse 2 → Bridge → Final Chorus → Outro\n[LANGUAGE] {language}\n[NOTE] Write the final lyric naturally in {language}; preserve the same story and emotional arc.\n[GENRE] {genre_text} + {accent_text}\n[CONTENT IDEA] {idea}"""


def artwork_prompts(title, lyric, dna, language, accents, style_name=None):
    # Generate 3 genuinely different concepts for the selected visual style.
    anchor = clean(re.sub(r"\[.*?\]", " ", lyric), 420)
    accent = ", ".join(accents) if accents else "Javanese nuance 5-10% only"
    variants = [
        ("A", "close-up character storytelling, intimate facial emotion, strong foreground/background separation"),
        ("B", "wider cinematic scene, environmental storytelling, dramatic perspective and depth"),
        ("C", "bold symbolic visual metaphor, unusual but coherent composition, memorable thumbnail silhouette"),
    ]
    style_map = dict(ART_VARIANTS)
    if style_name:
        chosen = style_name
        style = style_map.get(style_name, style_name)
    else:
        chosen = None
        style = "premium cinematic 3D"
    prompts=[]
    for letter, concept in variants:
        label = f"{chosen} — PROMPT {letter}" if chosen else f"ARTWORK — PROMPT {letter}"
        prompts.append((label, f"""Create a premium cinematic 3D music artwork for the song title \"{title}\".
Story anchor: {anchor}
Creative DNA: {dna}
Visual style: {style}.
Composition concept: {concept}.
Character: serious but subtly funny/absurd in a natural way; never childish, never random.
The visual must directly match the title and lyric story; no unrelated objects or themes.
Cultural accent: {accent}; keep Javanese influence subtle at approximately 5-10%, never the main theme.
Strong focal character, cinematic lighting, realistic 3D depth, premium composition, emotionally readable at thumbnail size.
Design a safe central composition that works for LONG 16:9 and SHORT 9:16 crops.
IMPORTANT: Keep the 3D GOKIL logo as a separate overlay asset; do not bake the logo into the artwork.
No watermark, no unnecessary text."""))
    return prompts


def seo_pack(title, keyword, idea, language, country, genres):
    if language == "English":
        desc = f"{title}\n\nAn original song built around: {idea}\n\nTarget: {country}\nGenres: {', '.join(genres)}\n\nThis is an original creative work inspired by the broader genre and audience signal, not a copy of another song."
        tags = [title, keyword, "metal music", "heavy metal", "love song", "rock music", country]
    else:
        desc = f"{title}\n\nLagu original dengan ide: {idea}\n\nTarget: {country}\nGenre: {', '.join(genres)}\n\nKarya original dengan identitas dan aransemen sendiri."
        tags = [title, keyword, "lagu", "musik", "rock", "metal", country]
    hashtags = " ".join("#" + re.sub(r"[^A-Za-z0-9]", "", x.replace(" ", "")) for x in tags[:8])
    return desc, ", ".join(dict.fromkeys(tags)), hashtags

# =========================================================
# AUDIO ANALYZER
# =========================================================
def analyze_audio(uploaded_file):
    if librosa is None or np is None:
        raise RuntimeError(f"Audio analyzer belum tersedia: {AUDIO_IMPORT_ERROR}")
    ext = os.path.splitext(uploaded_file.name)[1] or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as f:
        f.write(uploaded_file.getbuffer()); path=f.name
    try:
        y,sr=librosa.load(path,sr=22050,mono=True)
        if len(y)<sr*3: raise RuntimeError("Audio minimal sekitar 3 detik.")
        rms=librosa.feature.rms(y=y)[0]
        centroid=librosa.feature.spectral_centroid(y=y,sr=sr)[0]
        tempo,_=librosa.beat.beat_track(y=y,sr=sr)
        tempo=float(np.asarray(tempo).reshape(-1)[0])
        tempo=max(40,min(220,tempo))
        energy=round(float(np.clip((float(np.mean(rms))-.02)/.20,0,1)*100))
        if energy>=70 and tempo>=125: mood="Energetic / Aggressive"
        elif energy>=55: mood="Driving / Powerful"
        elif energy<35 and tempo<90: mood="Calm / Melancholic"
        else: mood="Emotional / Atmospheric"
        if tempo>=145 and energy>=65: genre="Rock / Metal / High Energy"
        elif 95<=tempo<=125: genre="Groove / Rock / Pop"
        elif tempo<95: genre="Ballad / Atmospheric"
        else: genre="Pop / Electronic"
        key_names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
        chroma=librosa.feature.chroma_stft(y=y,sr=sr).mean(axis=1)
        key=key_names[int(np.argmax(chroma))]
        return {"Duration":round(len(y)/sr,1),"BPM":round(tempo),"Energy":energy,"Genre estimate":genre,"Mood":mood,"Key estimate":key,"Spectral centroid":round(float(np.median(centroid)))}
    finally:
        try: os.remove(path)
        except OSError: pass

# =========================================================
# UI
# =========================================================
st.title("🎵 3D GOKIL MUSIC CONTENT FACTORY")
st.caption("Target → Genre Opportunity → Original Fusion → Content Idea → Click → Retention → Song → Artwork → SEO")

with st.sidebar:
    st.header("🧬 CHANNEL DNA")
    dna=st.text_area("DNA / tema channel", DEFAULT_DNA, height=100)
    country=st.selectbox("🌍 1. TARGET COUNTRY", list(COUNTRIES.keys()), index=0)
    st.caption("Negara ditentukan dulu. Setelah itu mesin mencari tema yang paling kuat di negara tersebut.")
    _, _, language=COUNTRIES[country]
    st.info(f"Bahasa output: **{language}**")
    base_group=st.selectbox("🎼 BASE GENRE", list(GENRE_GROUPS.keys()), index=0, help="Genre utama yang menjadi fondasi. Contoh US: Heavy Metal / Rock.")
    accent_groups=st.multiselect("🪕 ACCENT / FUSION TAMBAHAN", [g for g in GENRE_GROUPS.keys() if g != base_group], default=[], help="Contoh: BASE A + accent B + accent D = Metal + Modern Dangdut + Karawitan.")
    genre_groups=[base_group]
    accents=selected_genres(accent_groups)
    if accents:
        st.caption("Accent terpilih: " + ", ".join(accents))
    st.markdown("**Nuansa Jawa:** otomatis 5–10% sebagai aksen, bukan tema utama.")
    custom_topic=st.text_input("💡 Topik/keyword awal (opsional)", "")

# Main tabs
tabs=st.tabs(["📊 STRATEGY", "🎯 CLICK", "✍️ 5 LYRICS", "🎨 5 ARTWORK", "🎧 SUNO ANALYZER", "🚀 SEO"])

with tabs[0]:
    st.header("📊 Music Strategy")
    st.write("Kita mencari **genre yang punya signal kuat di target**, lalu memodifikasinya menjadi karya original. Angka Signal/Opportunity adalah skor internal riset, bukan search volume resmi YouTube.")
    st.subheader("1️⃣ TARGET → TEMA YANG DIMINATI")
    st.write("Pilih negara **lebih dulu**. Mesin tidak langsung mencari keyword acak; ia mencari beberapa tema besar yang paling kuat sebagai bahan pilihan.")
    if st.button("🔎 CARI TEMA TERKUAT DI TARGET", type="primary", use_container_width=True):
        with st.spinner(f"Mencari tema yang kuat di {country}..."):
            try:
                st.session_state.theme_rank = theme_research(country)
                st.session_state.selected_themes = []
                st.session_state.genre_rank = None
                st.session_state.research_result = None
                st.session_state.keyword_table = None
                st.session_state.content_ideas=[]
                st.session_state.titles=[]
                st.session_state.lyrics=[]
                st.session_state.artworks=[]
            except Exception as e:
                st.error(str(e))

    if st.session_state.theme_rank:
        st.subheader(f"🏆 Tema Opportunity — {country}")
        tdf=pd.DataFrame(st.session_state.theme_rank)
        st.dataframe(tdf, use_container_width=True, hide_index=True)
        st.caption("Opportunity/Views/Day = signal internal dari video yang ditemukan, **bukan angka search-volume resmi YouTube**.")
        theme_names=[x["Theme"] for x in st.session_state.theme_rank]
        default_theme=theme_names[:1]
        selected_themes=st.multiselect("🎯 Pilih tema yang memang mau kita kejar", theme_names, default=default_theme)
        st.session_state.selected_themes=selected_themes
        if selected_themes:
            st.success("Tema terpilih: " + " + ".join(selected_themes))

    st.subheader("2️⃣ GENRE OPPORTUNITY")
    if not st.session_state.selected_themes:
        st.info("Cari dan pilih tema dulu. Setelah itu baru genre/keyword research dijalankan.")
    elif st.button("🔥 ANALYZE GENRE + CARI KEYWORD DARI TEMA", type="primary", use_container_width=True):
        with st.spinner("Menganalisis genre dan keyword berdasarkan tema terpilih..."):
            try:
                if not genre_groups: raise RuntimeError("Pilih minimal satu genre group.")
                rank=genre_research(country)
                st.session_state.genre_rank=rank
                # IMPORTANT: keyword research is now driven by selected target themes, not arbitrary DNA text.
                base_terms=selected_genres(genre_groups)
                theme_query=" ".join(st.session_state.selected_themes)
                topic=clean(custom_topic)
                query_topics = theme_query + (" " + topic if topic else "")
                queries=[f"{query_topics} {g}" for g in base_terms[:8]]
                region, lang, _=COUNTRIES[country]
                res=research_queries(queries, region, lang, max_per=12)
                st.session_state.research_result=res
                st.session_state.keyword_table=keyword_candidates(res, base_terms, language)
                st.session_state.content_ideas=[]
                st.session_state.titles=[]
                st.session_state.lyrics=[]
                st.session_state.artworks=[]
            except Exception as e:
                st.error(str(e))

    if st.session_state.genre_rank:
        st.subheader(f"🏆 Genre Opportunity — {country}")
        df=pd.DataFrame(st.session_state.genre_rank)
        st.dataframe(df, use_container_width=True, hide_index=True)
        top=df.iloc[0]
        st.success(f"TOP SIGNAL: **{top['Genre Group']}** — Avg Opportunity {top['Avg Opportunity']}")
        st.caption("Ini menunjukkan peluang relatif dari hasil riset yang dikumpulkan, bukan klaim bahwa YouTube menyediakan angka search-volume tersebut.")

    if st.session_state.keyword_table:
        st.subheader("3️⃣ 🔎 KEYWORD SIGNAL — BERDASARKAN TEMA TERPILIH")
        st.info("Keyword di bawah ini bukan hasil tebak-tebakan. Mesin mengambilnya dari video yang ditemukan setelah **Target Country → Theme → Genre** dipilih.")
        st.dataframe(pd.DataFrame(st.session_state.keyword_table), use_container_width=True, hide_index=True)
        st.caption("Cara baca: Opportunity = performa relatif video yang mendukung istilah; Evidence = jumlah video pendukung; Signal = kekuatan gabungan kemunculan + performa. Pilih keyword yang relevan dengan DNA, bukan angka terbesar secara buta.")
        choices=[x["Keyword"] for x in st.session_state.keyword_table[:10]]
        selected_kw=st.selectbox("Pilih keyword untuk dibuatkan Content Ideas", choices, key="keyword_selector")
        st.session_state.selected_keyword=selected_kw
        if st.button("💡 GENERATE 5 CONTENT IDEAS", use_container_width=True):
            base=selected_genres(genre_groups)
            st.session_state.content_ideas=make_content_ideas(selected_kw,dna,base,accents,language)
            st.session_state.selected_idea=st.session_state.content_ideas[0]
    if st.session_state.content_ideas:
        st.subheader("💡 5 Content Ideas")
        for i,idea in enumerate(st.session_state.content_ideas,1):
            st.markdown(f"**{i}.** {idea}")
            if language == "English":
                id_ideas = make_content_ideas(selected_kw, dna, selected_genres(genre_groups), accents, "Bahasa Indonesia")
                st.caption("🇮🇩 Arti: " + id_ideas[i-1].split(" | Genre:")[0])
        idx=st.radio("Pilih Content Idea", list(range(1,len(st.session_state.content_ideas)+1)), format_func=lambda x: f"Idea {x}", horizontal=True)
        st.session_state.selected_idea=st.session_state.content_ideas[idx-1]
        if st.button("➡️ BUILD CLICK + SONG", type="primary", use_container_width=True):
            kw=selected_kw
            st.session_state.titles=make_titles(st.session_state.selected_idea,kw,language,selected_genres(genre_groups))
            st.session_state.selected_title=st.session_state.titles[0]
            st.session_state.lyrics=[lyric_from_idea(st.session_state.selected_title,st.session_state.selected_idea,v,language,selected_genres(genre_groups),accents) for v,_ in STYLE_VARIANTS]
            st.session_state.artworks=artwork_prompts(st.session_state.selected_title,st.session_state.lyrics[0],dna,language,accents,"02 — CINEMATIC")
            st.success("Strategy dibangun. Sekarang pilih Title, Lyric, dan Artwork.")

with tabs[1]:
    st.header("🎯 CLICK PACKAGE")
    if not st.session_state.titles:
        st.info("Pilih Content Idea di tab Strategy lalu tekan BUILD CLICK + SONG.")
    else:
        st.subheader("5 pilihan Title")
        chosen=st.radio("Pilih judul", st.session_state.titles, index=0)
        st.session_state.selected_title=chosen
        if language == "English":
            st.caption("🇮🇩 Arti judul: " + title_translation(chosen))
        st.write("**Kenapa harus diklik:** judul menjanjikan konflik/emosi yang jelas dan harus cocok dengan isi lagu.")
        st.subheader("🪝 Hook + Retention Structure")
        st.markdown("""
**0–5s — AUDIO HOOK:** masuk cepat, jangan intro kosong.

**5–20s — SETUP:** kenalkan konflik/emosi utama.

**20–45s — BUILD:** tambah detail dan ketegangan.

**CHORUS:** payoff pertama / hook utama.

**VERSE 2:** cerita berkembang, jangan mengulang persis.

**BRIDGE:** perubahan/kejutan emosional.

**FINAL CHORUS:** klimaks terbesar.

**OUTRO:** tutup singkat dengan rasa yang tertinggal.
""")
        st.success("Prinsipnya: CLICK → STAY → PAYOFF. YouTube sendiri mengelompokkan perjalanan penonton sebagai appeal, engagement, dan satisfaction; CTR membantu membaca daya tarik klik, sedangkan retention menunjukkan apakah penonton bertahan. citeturn0search7")

with tabs[2]:
    st.header("✍️ 5 LYRICS — PILIHAN")
    if not st.session_state.lyrics:
        st.info("Build dulu dari tab Strategy.")
    else:
        titles=st.session_state.titles
        selected_title=st.selectbox("Judul aktif", titles, index=titles.index(st.session_state.selected_title) if st.session_state.selected_title in titles else 0)
        st.session_state.selected_title=selected_title
        # regenerate five lyrics for current selected title
        st.session_state.lyrics=[lyric_from_idea(selected_title,st.session_state.selected_idea,v,language,selected_genres(genre_groups),accents) for v,_ in STYLE_VARIANTS]
        for i,((name,_),lyr) in enumerate(zip(STYLE_VARIANTS,st.session_state.lyrics),1):
            with st.expander(name, expanded=(i==1)):
                st.text_area(f"Lirik {i}", lyr, height=430, key=f"lyric_{i}")
                if language=="English":
                    id_title = title_translation(selected_title)
                    id_lyric = lyric_from_idea(id_title, st.session_state.selected_idea, v, "Bahasa Indonesia", selected_genres(genre_groups), accents)
                    with st.expander("🇮🇩 TERJEMAHAN / VERSI BAHASA INDONESIA"):
                        st.text_area(f"Terjemahan {i}", id_lyric, height=430, key=f"lyric_id_{i}")
        fusion = ", ".join(selected_genres(genre_groups) + accents)
        st.subheader("🎵 SUNO STYLE — hasil dari pilihan genre")
        st.code(f"{fusion}. Target language: {language}. 5-10% subtle Javanese/Nusantara accent. Strong audio hook, memorable chorus, dynamic build, original arrangement, cinematic production.\nDNA: {dna}")
        st.info(f"Bahasa lirik: **{language}**. Untuk target US/UK, lirik utama dibuat English; terjemahan Indonesia hanya diberikan sebagai bantuan memahami makna, bukan dimasukkan ke lirik final.")

with tabs[3]:
    st.header("🎨 ARTWORK PROMPT LAB")
    if not st.session_state.titles:
        st.info("Build dulu dari tab Strategy.")
    else:
        title=st.session_state.selected_title
        style_names=[name for name,_ in ART_VARIANTS]
        selected_style=st.selectbox("🎨 PILIH GAYA ARTWORK", style_names, index=1, key="art_style_choice")
        st.caption("Pilih satu gaya. Mesin akan membuat 3 konsep prompt berbeda agar kamu bisa memilih berdasarkan insting/mood.")
        if st.button("🎨 GENERATE 3 PROMPT", type="primary", use_container_width=True):
            lyric=st.session_state.lyrics[0] if st.session_state.lyrics else ""
            st.session_state.artworks=artwork_prompts(title,lyric,dna,language,accents,selected_style)
        # Generate for first view if none exists or style changed.
        if not st.session_state.artworks or not all(selected_style in x[0] for x in st.session_state.artworks):
            st.session_state.artworks=artwork_prompts(title,st.session_state.lyrics[0] if st.session_state.lyrics else "",dna,language,accents,selected_style)
        for i,(name,prompt) in enumerate(st.session_state.artworks,1):
            with st.expander(name, expanded=(i==1)):
                st.text_area(f"Prompt {i}",prompt,height=300,key="art_prompt_"+str(i))
                if st.button(f"✅ PILIH {name}", key="choose_art_"+str(i), use_container_width=True):
                    st.session_state["selected_artwork_prompt"] = prompt
                    st.session_state["selected_artwork_name"] = name
                    st.success(f"Artwork terpilih: {name}")
        if st.session_state.get("selected_artwork_name"):
            st.info("Artwork aktif: " + st.session_state["selected_artwork_name"])
        st.caption("Logo 3D GOKIL tidak dibakar ke gambar; render engine memasangnya sebagai overlay agar SHORT statis dan LONG bisa floating.")

with tabs[4]:
    st.header("🎧 SUNO / MUSIC ANALYZER")
    st.write("Upload referensi MP3/WAV untuk mendapatkan estimasi tempo, energy, genre family, mood, key, lalu gunakan hasilnya sebagai referensi — bukan penyalinan lagu.")
    uploaded=st.file_uploader("Upload MP3 / WAV / M4A / FLAC", type=["mp3","wav","m4a","flac"])
    if st.button("🔬 ANALYZE MUSIC", use_container_width=True):
        if not uploaded: st.warning("Upload audio dulu.")
        else:
            try:
                st.session_state.music_analysis=analyze_audio(uploaded)
            except Exception as e: st.error(str(e))
    if st.session_state.music_analysis:
        a=st.session_state.music_analysis
        st.dataframe(pd.DataFrame([a]), use_container_width=True, hide_index=True)
        st.subheader("Suno Style Reference")
        st.code(f"{a['Genre estimate']}, {a['Mood']}, {a['BPM']} BPM, cinematic production, strong chorus, memorable melody, original arrangement")
        st.caption("Analisis audio ini bersifat estimasi sinyal audio; bukan identifikasi instrumen/vokal yang sempurna.")

    st.divider()
    st.header("🎬 AUTO RENDER — LONG + SHORT")
    st.caption("Semua hasil render dipisahkan rapi: 3dgokil/long dan 3dgokil/short. Logo 3D GOKIL selalu terpasang; LONG floating, SHORT statis.")
    st.code("3dgokil/\n├── long/\n│   ├── video/\n│   ├── artwork/\n│   └── prompt/\n└── short/\n    ├── video/\n    ├── artwork/\n    └── prompt/", language="text")

    render_title = st.session_state.selected_title or "3D GOKIL SONG"
    artwork_options = [name for name, _ in st.session_state.artworks] if st.session_state.artworks else [
        "01 — SERIUS", "02 — CINEMATIC", "03 — SEMI-FUNNY", "04 — GOKIL", "05 — DARK / MYSTICAL"
    ]
    long_art = st.selectbox("🖼️ ARTWORK LONG", artwork_options, key="render_long_art")
    short_art = st.selectbox("🖼️ ARTWORK SHORT", artwork_options, key="render_short_art")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📺 LONG")
        long_spectrum = st.selectbox(
            "🎚️ MODEL SPECTRUM LONG",
            ["BALOK", "LINE", "CLINE", "P2P", "FIRE", "NONE"],
            index=0,
            key="long_spectrum",
        )
        st.caption("LONG saja: pilih model visual spectrum. SHORT tidak memakai spectrum.")
    with c2:
        st.subheader("📱 SHORT")
        short_hook = st.text_input(
            "🪝 Hook 0–5s",
            "Kalimat pembuka paling kuat dari lagu",
            key="short_hook",
        )
        short_cta = st.selectbox(
            "📣 CTA",
            ["Follow untuk lagu berikutnya", "Subscribe untuk full song", "Dengarkan versi LONG", "Tanpa CTA"],
            index=0,
            key="short_cta",
        )
        st.caption("SHORT: Hook + payoff cepat + CTA. Spectrum otomatis OFF.")

    render_ready = st.checkbox("✅ Saya siap render", value=False, key="render_ready")
    if st.button("🚀 SIAPKAN RENDER LONG + SHORT", type="primary", use_container_width=True):
        if not render_ready:
            st.warning("Centang 'Saya siap render' dulu.")
        else:
            import json
            render_config = {
                "TITLE": render_title,
                "LOGO": {
                    "ASSET": "3dgokil_logo.png",
                    "LONG": "FLOATING_SLOW",
                    "SHORT": "STATIC",
                },
                "LONG": {
                    "ARTWORK": long_art,
                    "ARTWORK_PROMPT": st.session_state.get("selected_artwork_prompt", ""),
                    "SPECTRUM": long_spectrum,
                    "OUTPUT": "3dgokil/long",
                },
                "SHORT": {
                    "ARTWORK": short_art,
                    "ARTWORK_PROMPT": st.session_state.get("selected_artwork_prompt", ""),
                    "HOOK": short_hook,
                    "CTA": short_cta,
                    "SPECTRUM": "NONE",
                    "OUTPUT": "3dgokil/short",
                },
            }
            st.session_state["render_config"] = render_config
            st.success("Render package siap: LONG + SHORT. LONG memakai spectrum pilihan; SHORT memakai Hook + CTA tanpa spectrum.")
            st.json(render_config)
            st.download_button(
                "⬇️ DOWNLOAD RENDER CONFIG",
                data=json.dumps(render_config, ensure_ascii=False, indent=2),
                file_name="render_config.json",
                mime="application/json",
                use_container_width=True,
            )

with tabs[5]:
    st.header("🚀 SEO OPTIMIZER")
    if not st.session_state.selected_title:
        st.info("Pilih Content Idea + Title dulu.")
    else:
        kw=st.session_state.selected_keyword or ""
        if not kw and st.session_state.keyword_table:
            kw=st.session_state.keyword_table[0]["Keyword"]
        idea=st.session_state.selected_idea or "original music content"
        desc,tags,hashtags=seo_pack(st.session_state.selected_title,kw,idea,language,country,selected_genres(genre_groups))
        st.subheader("Description")
        st.text_area("",desc,height=220)
        st.subheader("Tags")
        st.text_area("",tags,height=100)
        st.subheader("Hashtags")
        st.code(hashtags)
        if language=="English":
            st.caption("🇮🇩 Terjemahan inti: SEO ini menjelaskan lagu original berdasarkan ide, target, dan genre yang dipilih.")

st.divider()
st.caption("3D GOKIL Music Factory — fokus pada genre opportunity, original fusion, click, retention, payoff, multiple lyrics, multiple artwork, dan SEO.")
