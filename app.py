import streamlit as st
import re, json

st.set_page_config(
    page_title="3D GOKIL AI Music Factory V1.2 FINAL",
    page_icon="🔥",
    layout="wide"
)

# =========================================================
# 3D GOKIL CORE DNA
# =========================================================
DNA = "REALITA KEHIDUPAN DI BUMI"
DNA_RULE = (
    "Masalahnya serius. Ceritanya nyata. Cara menyampaikannya GOKIL. "
    "Humor berasal dari situasi, ironi, permainan kata, dan satire; bukan vulgar."
)

st.title("🔥 3D GOKIL AI MUSIC FACTORY V1.2 FINAL")
st.caption("V1 + Song Structure Engine + STORY/SUB-THEME LAB + GOKIL ENGINE + TITLE LAB")

st.info(
    "DNA 3D GOKIL: REALITA KEHIDUPAN DI BUMI → cerita nyata → sudut pandang serius tapi lucu → "
    "judul → lirik → Suno → artwork → YouTube SEO."
)

# =========================================================
# DATA
# =========================================================
CATEGORIES = {
    "💰 Ekonomi & Uang": [
        "Gaji dan tanggal tua", "Utang dan cicilan", "Harga kebutuhan naik",
        "Dompet kosong", "Paylater", "Bensin dan biaya hidup",
        "Kerja keras tapi uang cepat habis"
    ],
    "🏢 Dunia Kerja": [
        "Bos dan target", "Lembur", "Burnout", "Karyawan serba salah",
        "PHK dan ketidakpastian", "Meeting yang tidak ada habisnya",
        "Kerja sampai lupa waktu"
    ],
    "👨‍👩‍👧 Keluarga": [
        "Ayah dan perjuangan", "Ibu dan pengorbanan", "Anak dewasa",
        "Kebutuhan keluarga", "Orang tua menunggu", "Keluarga sederhana"
    ],
    "❤️ Cinta & Hubungan": [
        "Mantan muncul lagi", "Cinta sederhana", "Kesepian",
        "Hubungan toxic", "Cinta di warung kopi", "Chat tidak dibalas"
    ],
    "🏙️ Kehidupan Kota": [
        "Kemacetan", "Kota tidak pernah tidur", "Transportasi",
        "Hujan dan perjalanan", "Polusi", "Kesepian di tengah keramaian"
    ],
    "🧑‍🤝‍🧑 Sosial": [
        "Tetangga lebih tahu", "Teman palsu", "Gengsi",
        "Media sosial", "Tekanan sosial", "Orang suka menghakimi"
    ],
    "🌑 Sisi Gelap Kehidupan": [
        "Kecemasan", "Insomnia", "Takut masa depan",
        "Tekanan hidup", "Merasa tertinggal", "Berjuang tanpa terlihat"
    ],
}

STORIES = {
    "Gaji dan tanggal tua": [
        ("GAJI MASUK, GAJI HILANG",
         "Seorang pekerja menunggu tanggal gajian seperti menunggu hari raya. Begitu uang masuk, listrik, kontrakan, makan, bensin, cicilan, dan kebutuhan keluarga datang bergantian. Rekening baru sempat tersenyum sebelum kembali sepi."),
        ("GAJI CUMA NUMPANG LEWAT",
         "Gaji datang sebagai tamu yang sangat sopan: masuk, menyapa sebentar, lalu pergi membawa hampir semua temannya. Si pemilik rekening tetap harus bekerja sampai akhir bulan sambil berharap saldo tidak pingsan duluan."),
        ("TANGGAL TUA PUNYA CERITA",
         "Menjelang akhir bulan, kreativitas manusia meningkat drastis: masak seadanya, menunda belanja, menghitung bensin, dan berharap ada keajaiban sebelum tanggal gajian berikutnya.")
    ],
    "Utang dan cicilan": [
        ("UTANG DATANG BERTAMU",
         "Utang awalnya terasa seperti teman penolong. Masalahnya, teman ini rajin datang setiap bulan dan selalu membawa teman-teman baru bernama bunga, denda, dan cicilan."),
        ("CICILAN SELALU TEPAT WAKTU",
         "Gaji kadang terasa terlambat, tetapi cicilan tidak pernah lupa tanggal. Seseorang bekerja keras hanya untuk menjaga agar tagihan tidak berubah menjadi monster yang mengetuk pintu."),
        ("BARANG SUDAH TUA, CICILAN BELUM SELESAI",
         "Sebuah barang yang dulu dibeli karena terlihat keren mulai rusak sebelum cicilannya lunas. Pemiliknya akhirnya merawat bukan cuma barang, tetapi juga harapan.")
    ],
    "Harga kebutuhan naik": [
        ("HARGA NAIK, DOMPET TETAP",
         "Harga kebutuhan terus naik seperti sedang mengejar rekor, sementara penghasilan berjalan dengan kecepatan biasa. Menghitung uang akhirnya menjadi olahraga harian."),
        ("BELANJA SEDIKIT, BAYAR BANYAK",
         "Keranjang belanja terlihat kosong, tetapi total di kasir membuat mata terbuka lebar. Barang yang dulu terasa biasa kini seperti barang mewah."),
        ("MURAH DI INGATAN",
         "Seseorang mencoba mengingat harga masa lalu sambil menatap harga hari ini. Nostalgia ternyata bisa muncul hanya dari melihat struk belanja.")
    ],
    "Paylater": [
        ("BELANJA SEKARANG, PUSING NANTI",
         "Seseorang membeli kenyamanan hari ini dengan janji membayar berkali-kali besok. Semua terasa mudah sampai notifikasi tagihan mulai berbunyi."),
        ("PENYELAMAT YANG DATANG TERLAMBAT",
         "Paylater membantu saat uang tidak cukup, tetapi bulan berikutnya datang membawa tagihan. Yang tadinya solusi berubah menjadi pengingat bahwa masa depan juga punya rekening."),
        ("TAGIHAN PUNYA INGATAN PANJANG",
         "Barang sudah terlupakan, tetapi tagihan tetap datang dengan ingatan yang sangat baik.")
    ],
    "Kerja keras tapi uang cepat habis": [
        ("KERJA KERAS, UANG LEPAS",
         "Seorang pekerja merasa sudah memberikan hampir seluruh tenaganya, tetapi saldo tetap cepat menghilang. Ia mulai bertanya apakah rekeningnya punya pintu rahasia."),
        ("KERINGAT BANYAK, SALDO SEDIKIT",
         "Tenaga terkuras sepanjang bulan, tetapi saldo tidak ikut gemuk. Meski begitu, ia tetap bangun besok dan mencoba lagi."),
        ("GAJI DATANG, KEBUTUHAN MENUNGGU",
         "Gaji belum masuk saja kebutuhan sudah antre. Begitu uang datang, antrean berubah menjadi rombongan.")
    ],
    "Bos dan target": [
        ("BOS MINTA SENYUM",
         "Bos meminta karyawan selalu tersenyum meski target naik, deadline maju, dan saldo rekening lebih sering menangis. Di kantor semua harus terlihat baik-baik saja."),
        ("TARGET NAIK, MANUSIA TETAP MANUSIA",
         "Target bertambah setiap bulan seolah manusia punya baterai cadangan. Seorang karyawan mencoba bertahan tanpa berubah menjadi robot kantor."),
        ("MEETING SAMPAI LUPA KENAPA RAPAT",
         "Rapat dimulai untuk membahas satu hal, lalu berkembang menjadi lima hal, tiga tugas baru, dan satu rapat berikutnya.")
    ],
    "Lembur": [
        ("KANTOR JADI RUMAH KEDUA",
         "Seorang pekerja terlalu sering pulang malam sampai satpam lebih hafal wajahnya daripada tetangga rumahnya. Lembur menjadi rutinitas, tidur menjadi barang mewah."),
        ("PULANG MALAM, BESOK MASUK LAGI",
         "Hari selesai ketika kota hampir tidur, tetapi alarm pagi tetap berbunyi. Tubuh meminta istirahat, kalender meminta hadir."),
        ("LEMBUR LAGI, KAPAN HIDUP?",
         "Jam kerja melebar seperti karet. Seseorang mulai bertanya kapan waktu kerja selesai dan waktu hidup dimulai.")
    ],
    "Burnout": [
        ("TUBUH ONLINE, JIWA OFFLINE",
         "Seseorang tetap bekerja, membalas pesan, dan tersenyum, tetapi di dalam dirinya baterai sudah merah. Ia belajar bahwa manusia bukan perangkat yang bisa di-charge lima menit."),
        ("SENYUM KANTOR, KEPALA BERISIK",
         "Di depan rekan kerja semuanya tampak normal. Di kepala, deadline, tagihan, dan masalah pribadi sedang mengadakan konser."),
        ("BATERAI MANUSIA MERAH",
         "Semua orang meminta produktif, tetapi tubuh dan pikiran mulai meminta jeda.")
    ],
    "Ayah dan perjuangan": [
        ("AYAH BILANG TIDAK CAPEK",
         "Ayah pulang membawa wajah lelah tetapi tetap berkata tidak apa-apa. Sandalnya mungkin sudah ingin pensiun, tetapi ia masih berdiri demi keluarga."),
        ("AYAH DIAM, KEBUTUHAN BICARA",
         "Ayah jarang mengeluh. Tangannya yang kasar menjadi bukti bahwa cinta kadang tidak banyak bicara, tetapi rajin membayar kebutuhan rumah."),
        ("SANDAL AYAH MINTA PENSIUN",
         "Sandal yang sudah lama menemani kerja mungkin sudah waktunya pensiun, tetapi pemiliknya belum boleh menyerah karena rumah masih membutuhkan perjuangannya.")
    ],
    "Ibu dan pengorbanan": [
        ("IBU SELALU BILANG CUKUP",
         "Ibu sering mengatakan dirinya tidak membutuhkan apa-apa, sementara diam-diam ia selalu mendahulukan kebutuhan keluarga."),
        ("DAPUR KECIL, CINTA BESAR",
         "Di dapur sederhana, ibu membuat makanan seadanya terasa seperti pesta. Ada lelah, humor kecil, dan cinta yang tidak pernah masuk laporan keuangan."),
        ("IBU MAKAN TERAKHIR",
         "Ketika makanan terbatas, ibu sering memastikan semua orang sudah makan sebelum memikirkan dirinya sendiri.")
    ],
    "Mantan muncul lagi": [
        ("MANTAN DATANG MEMBAWA NOTIFIKASI",
         "Saat hidup mulai tenang, sebuah notifikasi muncul dari nama yang seharusnya sudah menjadi sejarah. Jantung dan logika langsung mengadakan rapat darurat."),
        ("KATANYA CUMA MAU TANYA KABAR",
         "Satu pesan sederhana membuka kembali folder kenangan yang sudah lama dikunci. Masalahnya, perasaan ternyata belum ikut logout."),
        ("NOMOR LAMA, MASALAH BARU",
         "Sebuah nomor lama muncul lagi dan membuat seseorang bertanya apakah masa lalu memang punya fitur comeback.")
    ],
    "Tetangga lebih tahu": [
        ("TETANGGA LEBIH TAHU",
         "Tetangga tahu kapan seseorang pulang, beli apa, dan siapa yang datang. Kadang informasi tentang hidup sendiri terasa kalah cepat dibanding grup warga."),
        ("RADAR TETANGGA 24 JAM",
         "Tidak perlu CCTV mahal. Di beberapa lingkungan, radar tetangga sudah bekerja tanpa listrik tambahan."),
        ("KAMU TAHU DARI MANA?",
         "Seseorang baru sadar bahwa berita tentang dirinya sudah beredar sebelum ia sendiri sempat memahami kejadiannya.")
    ],
    "Teman palsu": [
        ("SENYUM DEPAN, CERITA BELAKANG",
         "Seseorang mulai sadar bahwa tidak semua tawa berarti persahabatan. Ada yang ramah di depan dan sangat kreatif di belakang."),
        ("TEMAN SAAT ADA MAUNYA",
         "Saat ada keuntungan semua datang membawa senyum. Saat masalah datang, grup mendadak sunyi seperti jaringan sedang hilang."),
        ("GRUP RAMAI, SAAT SUSAH SUNYI",
         "Ketika semuanya menyenangkan, pesan tidak pernah berhenti. Ketika masalah datang, notifikasi mendadak ikut pensiun.")
    ],
    "Media sosial": [
        ("LIKE BANYAK, TENANG SEDIKIT",
         "Notifikasi bertambah, tetapi rasa tenang tidak otomatis ikut naik. Validasi digital ternyata tidak bisa membayar semua masalah nyata."),
        ("HIDUP TERLIHAT SEMPURNA DI LAYAR",
         "Di media sosial semua orang tampak sukses. Di balik layar, sebagian masih menghitung tagihan dan bertanya apakah hidupnya tertinggal."),
        ("ONLINE TERUS, BAHAGIA KAPAN?",
         "Seseorang terus mencari validasi di layar sambil lupa memeriksa keadaan dirinya sendiri.")
    ],
    "Kecemasan": [
        ("KEPALA TIDAK PERNAH TIDUR",
         "Tubuh berbaring, tetapi pikiran masih bekerja lembur memikirkan uang, keluarga, pekerjaan, dan masa depan."),
        ("BESOK BELUM DATANG, SUDAH DICEMASKAN",
         "Seseorang mencoba menikmati hari ini, tetapi pikirannya sudah membayar masalah yang bahkan belum terjadi."),
        ("PIKIRAN LEMBUR TANPA GAJI",
         "Kepala terus memutar kemungkinan buruk tanpa pernah menerima uang lembur.")
    ],
    "Kesepian di tengah keramaian": [
        ("KOTA RAMAI, HATI SEPI",
         "Jutaan orang berlalu-lalang, tetapi seseorang tetap pulang membawa percakapan yang tidak pernah terjadi."),
        ("BANYAK TEMAN DI LAYAR, TETAP SENDIRIAN",
         "Kontak di ponsel penuh, tetapi ketika malam tiba, tidak semua nama bisa menjadi tempat pulang."),
        ("RAMAI DI LUAR, SUNYI DI DALAM",
         "Kota tidak pernah diam, tetapi seseorang bisa tetap merasa sendirian di tengah jutaan suara.")
    ],
}

# =========================================================
# HELPERS
# =========================================================
def generic_stories(sub):
    return [
        (f"{sub.upper()} — SISI YANG TIDAK KELIHATAN",
         f"Di balik {sub.lower()}, ada manusia biasa yang mencoba bertahan menghadapi kebutuhan, tekanan, dan kenyataan sehari-hari. Masalahnya serius, tetapi ia masih bisa menertawakan absurditas hidup."),
        (f"{sub.upper()} — KALAU HIDUP PUNYA SELERA HUMOR",
         f"{sub} terasa berat, tetapi hidup sering punya cara aneh untuk membuatnya semakin lucu. Tokoh utama mencoba tetap waras sambil menghadapi kejadian yang sangat manusiawi."),
        (f"{sub.upper()} — SERIUS, TAPI JANGAN LUPA KETAWA",
         f"Sebuah cerita tentang {sub.lower()} dari sudut pandang orang biasa: ada konflik nyata, ironi, kejadian kocak, dan pesan bahwa bertahan hidup tidak harus selalu dengan wajah muram.")
    ]

def title_candidates(story_title, target, tone):
    base = story_title.upper()
    local = [
        base, "HIDUP BEGINI AMAT", "SERIOUS AMAT, HIDUP?",
        "KETAWA DULU, HIDUP NANTI", "MASALAH DATANG, SENYUM BELAKANG",
        "HIDUP KERAS, KITA GASS", "REALITA YANG BIKIN NGAKAK"
    ]
    hybrid = [
        f"{base} | 3D GOKIL",
        f"{base} | REAL LIFE",
        f"REAL LIFE, REAL PROBLEM | {base}",
        f"{base} | SERIOUS BUT GOKIL",
        f"3D GOKIL — {base}"
    ]
    global_ = [
        "REAL LIFE, SERIOUSLY?", "LIFE IS WEIRD",
        "BROKE BUT STILL STANDING", "WORK HARD, LAUGH HARDER",
        "WHEN REAL LIFE GETS WEIRD", "SERIOUS PROBLEMS, GOKIL LIFE"
    ]
    if tone == "Satire":
        local += ["SIAPA SURUH HIDUP MAHAL?", "KETAWA DULU, BAYAR NANTI"]
        hybrid += ["REAL LIFE, REAL PAIN, REAL LAUGH", "SERIOUS PROBLEM, GOKIL RESPONSE"]
    elif tone == "Emotional":
        local += ["KITA MASIH BERTAHAN", "MESKI BERAT, TETAP JALAN", "DI BALIK SENYUM"]
        hybrid += ["STILL STANDING | KITA MASIH BERTAHAN", "BEHIND THE SMILE | DI BALIK SENYUM"]
    elif tone == "Rebellious":
        local += ["JANGAN SURUH KAMI DIAM", "KITA BUKAN MESIN"]
        hybrid += ["WE ARE NOT MACHINES | KITA BUKAN MESIN"]
    if target == "Lokal Indonesia":
        pool = local
    elif target == "Global":
        pool = global_
    else:
        pool = local + hybrid + global_
    return list(dict.fromkeys(pool))[:15]

def score_title(title, story_title, target):
    words = re.findall(r"[A-Za-z0-9]+", title)
    hook = 10 if len(title) <= 32 else 8 if len(title) <= 48 else 6
    remember = 10 if len(words) <= 5 else 8 if len(words) <= 8 else 6
    clarity = 10 if any(x in title for x in story_title.upper().split()[:2]) else 7
    family = 10
    local = 10 if any(x in title for x in [
        "GAJI","HIDUP","UTANG","BOS","SENYUM","DOMPET","TETANGGA",
        "AYAH","IBU","KERAS","CICILAN","MANTAN"
    ]) else 6
    global_ = 10 if any(x in title for x in [
        "REAL LIFE","LIFE","WORK","BROKE","STANDING","SMILE","SERIOUS"
    ]) else 6
    musical = 10 if 2 <= len(words) <= 7 else 7
    audience = local if target == "Lokal Indonesia" else global_ if target == "Global" else max(local, global_)
    return min(50, hook + remember + clarity + family + audience + musical)

def generate_lyrics(title, story, tone):
    return f"""[Intro — Overture & Audio Hook 0:00–0:05]
[Direct shout + strong guitar + kendang]
HEY! {title.upper()}!

[Verse 1 — 0:05–0:30]
{story}
Kita jalan, kita tahan
Meski hidup kadang kelewatan

[Pre-Chorus — 0:30–0:45]
Kalau berat, jangan hilang
Tarik napas, tetap berjuang
Kita manusia, bukan mesin
Masih berdiri, masih yakin

[Chorus / Main Hook — starts by 0:45]
HIDUP SERIUS, TAPI GOKIL!
Masalah datang, kita senyum kecil
HIDUP SERIUS, TAPI GOKIL!
Jatuh sekali, bangkit lagi!

[Verse 2]
Tagihan datang, deadline mengejar
Kepala panas, tetap sadar
Dunia kadang tidak masuk akal
Kita tertawa biar tidak tinggal

[Bridge — Mystical]
[Gamelan + suling bambu + ruang vokal]
Di balik tawa ada cerita
Di balik keras ada manusia
We keep moving, we keep fighting
Still alive, still surviving

[Final Chorus]
HIDUP SERIUS, TAPI GOKIL!
Masalah datang, kita senyum kecil
HIDUP SERIUS, TAPI GOKIL!
Belum selesai — GAS LAGI!

[Outro & Retention Loop]
[Instrumental hit]
Serius...
tapi GOKIL...
{title.upper()}...
GASS LAGI!"""

def suno_style():
    return """Modern Indonesian Cyber-Mystic Rock Dangdut, heavy rock energy,
powerful slightly raspy male vocal, immediate vocal/audio hook within first 5 seconds,
explosive opening, catchy sing-along chorus, tight distorted electric guitar,
energetic dangdut kendang groove, controlled deep bass, subtle electronic remix,
dramatic Javanese gamelan and bamboo flute accents, cinematic mystical atmosphere,
serious real-life Indonesian social satire with witty humor, relatable everyday life,
all-ages friendly, emotional but energetic, strong final chorus, replayable ending,
3:20–3:40, no long intro, no excessive instrumental solo, no extreme screaming,
no muddy bass, no overcrowded arrangement, no excessive EDM."""

def artwork_prompt(title, story, ratio):
    return f"""Cinematic 3D social-realism Indonesian music artwork, {ratio} composition.
Title: "{title}".
Story: {story}
Serious real-life situation with subtle visual humor and ironic details, not cartoonish.
Indonesian urban/cultural details, cyber-mystical atmosphere, neon green, deep crimson red,
black shadows, chrome highlights, cinematic lighting, realistic 3D texture, dramatic depth.
Strong focal character and visual storytelling.
Distressed chrome-metal title typography positioned TOP-LEFT: "{title}".
Small "3D GOKIL". No extra text, no watermark, no logos."""

# =========================================================
# STATE
# =========================================================
if "stories" not in st.session_state:
    st.session_state.stories = []
if "story_index" not in st.session_state:
    st.session_state.story_index = 0
if "titles" not in st.session_state:
    st.session_state.titles = []
if "final_title" not in st.session_state:
    st.session_state.final_title = ""

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("🔥 GOKIL ENGINE")
    gokil_level = st.slider(
        "GOKIL Level", 1, 5, 3,
        help="1 humor ringan • 3 satire kuat • 5 absurd/dark comedy"
    )
    all_ages = st.checkbox("🛡️ All Ages / Family Safe", True)
    st.caption("Humor fokus pada situasi, ironi, satire, dan permainan kata.")

# =========================================================
# TABS
# =========================================================
tabs = st.tabs([
    "🎭 STORY / SUB-THEME LAB",
    "🎯 TITLE LAB",
    "✍️ LYRIC LAB",
    "🎸 SUNO STYLE",
    "🖼️ ARTWORK",
    "🚀 YOUTUBE SEO"
])

# ---------------------------------------------------------
# STORY LAB
# ---------------------------------------------------------
with tabs[0]:
    st.header("🎭 Story / Sub-Theme Lab")
    st.write("Mulai dari DNA 3D GOKIL. Jangan langsung mengejar judul.")

    dna = st.text_input("DNA Utama", DNA)
    category = st.selectbox("Kategori Realita", list(CATEGORIES.keys()))
    subtheme = st.selectbox("Sub-Tema Spesifik", CATEGORIES[category])
    custom_subtheme = st.text_input("Sub-tema custom (opsional)")
    chosen_subtheme = custom_subtheme.strip() or subtheme

    if st.button("🔥 GENERATE CERITA GOKIL", use_container_width=True):
        st.session_state.stories = STORIES.get(chosen_subtheme, generic_stories(chosen_subtheme))
        st.session_state.story_index = 0
        st.session_state.final_title = ""
        st.session_state.titles = []
        st.session_state.dna = dna
        st.session_state.subtheme = chosen_subtheme

    if st.session_state.stories:
        st.success(
            f"DNA: {st.session_state.get('dna', DNA)} | "
            f"Sub-tema: {st.session_state.get('subtheme', chosen_subtheme)} | "
            f"GOKIL Level: {gokil_level}"
        )

        for i, (story_title, story_body) in enumerate(st.session_state.stories):
            with st.container(border=True):
                st.markdown(f"### {i+1:02d}. {story_title}")
                st.write(story_body)
                if st.button(f"👉 PILIH CERITA {i+1:02d}", key=f"story_{i}"):
                    st.session_state.story_index = i
                    st.session_state.final_title = ""
                    st.session_state.titles = []

        selected = st.session_state.stories[st.session_state.story_index]
        st.session_state.story_title = selected[0]
        st.session_state.story_body = selected[1]
        st.success(f"✅ Cerita aktif: {selected[0]}")

# ---------------------------------------------------------
# TITLE LAB
# ---------------------------------------------------------
with tabs[1]:
    st.header("🎯 Title Lab")
    story_title = st.text_input(
        "Cerita / angle",
        value=st.session_state.get("story_title", "")
    )
    target = st.selectbox(
        "Target",
        ["Lokal Indonesia", "Local + Global", "Global"]
    )
    title_tone = st.selectbox(
        "Tone",
        ["Auto", "Satire", "Emotional", "Rebellious"]
    )

    if st.button("🚀 GENERATE PILIHAN JUDUL", use_container_width=True):
        if not story_title.strip():
            st.warning("Pilih cerita terlebih dahulu.")
        else:
            st.session_state.titles = title_candidates(
                story_title, target, title_tone
            )

    if st.session_state.titles:
        scored = [
            (t, score_title(t, story_title, target))
            for t in st.session_state.titles
        ]
        scored.sort(key=lambda x: x[1], reverse=True)

        for i, (title, score) in enumerate(scored):
            st.markdown(f"**{i+1}. {title}** — `{score}/50`")
            if st.button(f"✅ GUNAKAN JUDUL #{i+1}", key=f"title_{i}"):
                st.session_state.final_title = title

        if st.session_state.final_title:
            st.success(f"🔥 JUDUL AKTIF: {st.session_state.final_title}")

        st.caption(
            "Title Score adalah heuristic internal untuk membantu memilih kemasan judul. "
            "Bukan jaminan ranking atau viral."
        )

# ---------------------------------------------------------
# LYRIC LAB
# ---------------------------------------------------------
with tabs[2]:
    st.header("✍️ Lyric Lab — Song Structure Engine V1.1")
    st.markdown("""
**Struktur inti:**
- **0:00–0:05** Overture & Audio Hook
- **0:05–0:30** Verse 1
- **0:30–0:45** Pre-Chorus
- **mulai 0:45** Chorus / Main Hook
- Verse 2
- Bridge — mystical
- Final Chorus
- Outro & Retention Loop
""")

    active_title = st.text_input(
        "Judul Lagu",
        value=st.session_state.get("final_title", st.session_state.get("story_title", ""))
    )
    active_story = st.session_state.get("story_body", "")

    if st.button("🎤 GENERATE LIRIK V1.1", use_container_width=True):
        if active_title.strip():
            st.session_state.lyrics = generate_lyrics(
                active_title, active_story, title_tone if "title_tone" in locals() else "Auto"
            )
        else:
            st.warning("Pilih judul terlebih dahulu.")

    lyrics = st.text_area(
        "Lyrics — EDITABLE",
        value=st.session_state.get("lyrics", ""),
        height=520
    )
    st.session_state.lyrics = lyrics

# ---------------------------------------------------------
# SUNO
# ---------------------------------------------------------
with tabs[3]:
    st.header("🎸 Suno Style — 3D GOKIL DNA")
    st.code(suno_style())
    st.caption("Style mengutamakan hook cepat, identitas Indonesian Cyber-Mystic Rock Dangdut, dan GOKIL satire.")

# ---------------------------------------------------------
# ARTWORK
# ---------------------------------------------------------
with tabs[4]:
    st.header("🖼️ Artwork Prompt")
    art_title = st.session_state.get("final_title", st.session_state.get("story_title", "JUDUL LAGU"))
    art_story = st.session_state.get("story_body", "realita kehidupan di bumi")
    st.markdown("**LONG — 16:9**")
    st.code(artwork_prompt(art_title, art_story, "16:9"))
    st.markdown("**SHORT — 9:16**")
    st.code(artwork_prompt(art_title, art_story, "9:16"))

# ---------------------------------------------------------
# SEO
# ---------------------------------------------------------
with tabs[5]:
    st.header("🚀 YouTube SEO")
    seo_title = st.session_state.get("final_title", st.session_state.get("story_title", "JUDUL LAGU"))
    seo_story = st.session_state.get("story_body", "")
    description = f"""{seo_title} | 3D GOKIL

Realita kehidupan di bumi, diceritakan serius tetapi tetap GOKIL.

{seo_story}

🔥 3D GOKIL — Indonesian Cyber-Mystic Rock Dangdut.

#3DGOKIL #MusikIndonesia #RockDangdut #DangdutModern #IndonesianMusic"""

    st.text_input("YouTube Title", value=seo_title)
    st.text_area("Description", value=description, height=250)
    st.text_input(
        "Hashtags",
        value="#3DGOKIL #MusikIndonesia #RockDangdut #DangdutModern #IndonesianMusic"
    )
    st.caption(
        "SEO helper ini fokus pada kejelasan topik dan packaging. Jangan menganggap tags sebagai faktor utama discovery."
    )

st.divider()
st.caption("3D GOKIL AI Music Factory V1.2 FINAL • V1 + V1.1 + Story/GOKIL + Title Lab")
