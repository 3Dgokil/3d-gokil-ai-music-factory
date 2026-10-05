import streamlit as st
import re, json

st.set_page_config(
    page_title="3D GOKIL AI Music Factory V1.4",
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

st.title("🔥 3D GOKIL AI MUSIC FACTORY V1.4")
st.caption("V1 + Song Structure Engine + DYNAMIC DNA + STORY/SUB-THEME LAB + GOKIL ENGINE + TITLE LAB")
st.success("🔥 V1.4 — DYNAMIC DNA / CATEGORY ENGINE + 10 STORY ENGINE")

st.info(
    "DNA 3D GOKIL: DNA → UNIVERSE → KATEGORI → SUB-TEMA → CERITA → "
    "serius + relatable + GOKIL → judul → lirik → Suno → artwork → YouTube SEO."
)

# =========================================================
# DATA
# =========================================================
# =========================================================
# DYNAMIC DNA / UNIVERSE ENGINE
# =========================================================
# The selected DNA is the universe. Categories and sub-themes are derived
# from it, so changing DNA changes the story world instead of only changing
# the label at the top of the screen.

BASE_BUMI = {
    "💰 Ekonomi & Uang": ["Gaji dan tanggal tua", "Utang dan cicilan", "Harga kebutuhan naik", "Dompet kosong", "Paylater", "Bensin dan biaya hidup", "Kerja keras tapi uang cepat habis"],
    "🏢 Dunia Kerja": ["Bos dan target", "Lembur", "Burnout", "Karyawan serba salah", "PHK dan ketidakpastian", "Meeting yang tidak ada habisnya", "Kerja sampai lupa waktu"],
    "👨‍👩‍👧 Keluarga": ["Ayah dan perjuangan", "Ibu dan pengorbanan", "Anak dewasa", "Kebutuhan keluarga", "Orang tua menunggu", "Keluarga sederhana"],
    "❤️ Cinta & Hubungan": ["Mantan muncul lagi", "Cinta sederhana", "Kesepian", "Hubungan toxic", "Cinta di warung kopi", "Chat tidak dibalas"],
    "🏙️ Kehidupan Kota": ["Kemacetan", "Kota tidak pernah tidur", "Transportasi", "Hujan dan perjalanan", "Polusi", "Kesepian di tengah keramaian"],
    "🧑‍🤝‍🧑 Sosial": ["Tetangga lebih tahu", "Teman palsu", "Gengsi", "Media sosial", "Tekanan sosial", "Orang suka menghakimi"],
    "🌑 Sisi Gelap Kehidupan": ["Kecemasan", "Insomnia", "Takut masa depan", "Tekanan hidup", "Merasa tertinggal", "Berjuang tanpa terlihat"],
}

DYNAMIC_UNIVERSES = [
    {
        "name": "🌍 Realita Kehidupan di Bumi",
        "match": ["bumi", "dunia nyata", "realita kehidupan"],
        "categories": BASE_BUMI,
        "description": "Manusia, ekonomi, keluarga, kerja, hubungan, sosial, dan perjuangan sehari-hari."
    },
    {
        "name": "🌓 Realita Kehidupan di 2 Dimensi",
        "match": ["2 dimensi", "2d", "dua dimensi", "dimensi 2"],
        "categories": {
            "🎨 Dunia Karakter 2D": ["Karakter hidup di gambar", "Tokoh utama dan tokoh sampingan", "Karakter yang ingin keluar frame", "Dunia tanpa volume", "Nasib karakter latar", "Kehidupan setelah layar dimatikan"],
            "🖼️ Realita vs Gambar": ["Dunia nyata vs dunia gambar", "Warna hilang dari dunia", "Garis dan batas kehidupan", "Objek yang hanya ada di frame", "Manusia menjadi ilustrasi", "Hidup di dalam poster"],
            "⚡ Glitch & Absurd": ["Glitch kehidupan", "Frame rusak", "Loop tanpa akhir", "NPC mulai sadar", "Dialog yang salah", "Dunia loading terus"],
            "🏙️ Kota 2D": ["Kota datar", "Jalan tanpa ujung", "Gedung hanya latar", "Transportasi dalam frame", "Hujan yang selalu berulang", "Malam yang tidak pernah berganti"],
            "😂 GOKIL 2D": ["Karakter serius tapi absurd", "Masalah tidak punya dimensi", "Bos dalam dunia 2D", "Dompet 2D", "Cinta beda frame", "Tetangga satu layer"],
        },
        "description": "Universe visual 2D: karakter, frame, layer, glitch, dunia gambar, dan ironi kehidupan datar."
    },
    {
        "name": "🌐 Realita Kehidupan Digital",
        "match": ["digital", "internet", "online", "dunia maya", "media sosial"],
        "categories": {
            "📱 Identitas Online": ["Hidup di balik username", "Avatar vs manusia asli", "Jejak digital", "Akun kedua", "Online tapi kesepian", "Validasi dari layar"],
            "🤖 AI & Algoritma": ["Manusia vs AI", "Algoritma menentukan nasib", "Rekomendasi tidak masuk akal", "Kerja digantikan mesin", "AI jadi teman", "Prompt kehidupan"],
            "📈 Dunia Viral": ["Mengejar viral", "Like dan komentar", "Konten demi algoritma", "Influencer kelelahan", "Drama jadi tontonan", "Viral sehari, lupa selamanya"],
            "💻 Ekonomi Digital": ["Kerja online", "Freelancer dan deadline", "Dompet digital", "Belanja satu klik", "Langganan tak berujung", "Uang hilang lewat notifikasi"],
            "🌑 Sisi Gelap Digital": ["FOMO", "Cyberbullying", "Kecanduan layar", "Privasi hilang", "Overthinking karena chat", "Hidup dibandingkan feed"],
        },
        "description": "Universe internet, AI, algoritma, media sosial, ekonomi digital, identitas online, dan kehidupan virtual."
    },
    {
        "name": "🚀 Realita Kehidupan Masa Depan",
        "match": ["masa depan", "future", "futuristik", "abad 22", "tahun 2050", "tahun 2100"],
        "categories": {
            "🤖 Manusia & Mesin": ["Robot mengambil pekerjaan", "AI jadi bos", "Manusia kalah cepat", "Robot minta cuti", "Teman virtual", "Manusia upgrade diri"],
            "🏙️ Kota Masa Depan": ["Kota pintar", "Transportasi otomatis", "Rumah tanpa manusia", "Gedung hidup sendiri", "Kemacetan algoritmik", "Hujan buatan"],
            "💳 Ekonomi Masa Depan": ["Gaji digital", "Uang tanpa uang", "Utang masa depan", "Langganan hidup", "Kerja tanpa kantor", "Harga oksigen"],
            "❤️ Hubungan Masa Depan": ["Cinta dengan AI", "Mantan digital", "Keluarga virtual", "Kencan hologram", "Kesepian di kota pintar", "Teman dari server"],
            "🌌 Sisi Gelap Masa Depan": ["Manusia kehilangan privasi", "Ingatan disimpan mesin", "Tubuh dan teknologi", "Hidup terlalu lama", "Dunia terlalu otomatis", "Manusia lupa cara sederhana"],
        },
        "description": "Universe futuristik: AI, robot, kota pintar, ekonomi baru, hubungan baru, dan masalah manusia yang tetap manusia."
    },
    {
        "name": "⚔️ Manusia vs Teknologi",
        "match": ["manusia vs teknologi", "manusia melawan teknologi", "teknologi vs manusia", "human vs tech"],
        "categories": {
            "🤖 Perebutan Pekerjaan": ["AI mengambil pekerjaan", "Robot lebih produktif", "Karyawan vs algoritma", "Bos lebih percaya mesin", "Manusia minta kesempatan", "Kerja bersama robot"],
            "🧠 Pikiran vs Algoritma": ["Algoritma tahu terlalu banyak", "Pilihan hidup direkomendasikan", "Otak manusia vs mesin", "Keputusan otomatis", "Prediksi masa depan", "Manusia tidak bisa logout"],
            "📱 Ketergantungan": ["Tanpa HP satu hari", "GPS menentukan hidup", "Notifikasi mengatur waktu", "Chat menggantikan bicara", "Search engine jadi guru", "Lupa nomor sendiri"],
            "❤️ Relasi Manusia-Mesin": ["AI jadi teman", "Robot jadi pasangan", "Chatbot tempat curhat", "Cemburu pada algoritma", "Teman manusia makin sedikit", "Cinta tanpa sentuhan"],
            "😂 Teknologi Bikin GOKIL": ["Mesin lebih drama dari manusia", "Robot ikut meeting", "AI salah paham", "Update bikin panik", "Password terlalu banyak", "Internet mati saat penting"],
        },
        "description": "Konflik dan kerja sama manusia dengan teknologi, dengan humor dan satire tetap menjadi ciri 3D GOKIL."
    },
    {
        "name": "🌑 Realita Mistis & Kehidupan Malam",
        "match": ["mistis", "misteri", "horor", "gaib", "kehidupan malam", "dunia gaib"],
        "categories": {
            "👻 Kehidupan Setelah Tengah Malam": ["Tetangga misterius", "Warung tengah malam", "Kos yang terlalu sunyi", "Suara dari kamar kosong", "Pulang kerja jam tiga", "Lampu jalan terakhir"],
            "🕯️ Ritual & Tradisi": ["Ritual keluarga", "Pantangan kampung", "Benda warisan", "Pesan orang tua", "Malam tertentu", "Rahasia rumah lama"],
            "🏙️ Horor Kehidupan Nyata": ["Tagihan lebih menakutkan", "Bos muncul saat lembur", "Saldo tengah malam", "Chat dari nomor lama", "Lift berhenti sendiri", "Motor mogok di jalan sepi"],
            "🧿 Mitos Modern": ["Pesugihan digital", "Dukun online", "Jimat virtual", "Algoritma seperti mantra", "Viral karena ritual", "Aplikasi pemanggil nasib"],
            "😂 Mistis Tapi GOKIL": ["Setan ikut antre", "Hantu takut tagihan", "Pocong cari Wi-Fi", "Jin ikut lembur", "Makhluk gaib punya cicilan", "Dunia gaib kena deadline"],
        },
        "description": "Mistis, misteri, kehidupan malam, dan horor sosial dengan sentuhan GOKIL—bukan sekadar horor kosong."
    },
]

def get_dynamic_universe(dna_text):
    text = (dna_text or "").strip().lower()
    # Specific concepts first, broad 'bumi' last.
    for universe in DYNAMIC_UNIVERSES[1:]:
        if any(k in text for k in universe["match"]):
            return universe
    return DYNAMIC_UNIVERSES[0]

def get_dynamic_categories(dna_text):
    text = (dna_text or "").strip().lower()
    universe = get_dynamic_universe(text)
    if universe is not DYNAMIC_UNIVERSES[0]:
        return universe
    # For an unknown DNA, derive a small generic category system from the words.
    if text and text not in [k.lower() for k in DYNAMIC_UNIVERSES[0]["match"]]:
        return {
            "name": f"🧬 Universe Custom — {dna_text.strip()}",
            "description": f"Universe khusus berdasarkan DNA: {dna_text.strip()}.",
            "categories": {
                "🎯 Inti Masalah": [f"Konflik utama {dna_text.strip()}", f"Sisi tersembunyi {dna_text.strip()}", f"Dampak {dna_text.strip()}", f"Manusia di dalam {dna_text.strip()}", f"Perubahan karena {dna_text.strip()}", f"Krisis {dna_text.strip()}"],
                "🧑‍🤝‍🧑 Manusia & Relasi": [f"Keluarga dan {dna_text.strip()}", f"Pertemanan dan {dna_text.strip()}", f"Cinta dan {dna_text.strip()}", f"Kerja dan {dna_text.strip()}", f"Masyarakat dan {dna_text.strip()}", f"Kesepian dalam {dna_text.strip()}"],
                "⚡ Konflik & Konsekuensi": [f"Harga yang dibayar untuk {dna_text.strip()}", f"Kesalahan karena {dna_text.strip()}", f"Pilihan sulit dalam {dna_text.strip()}", f"Ketergantungan pada {dna_text.strip()}", f"Batas {dna_text.strip()}", f"Masa depan {dna_text.strip()}"],
                "😂 GOKIL Angle": [f"Ironi {dna_text.strip()}", f"Sisi absurd {dna_text.strip()}", f"Hal lucu dari {dna_text.strip()}", f"Satire tentang {dna_text.strip()}", f"Kesialan karena {dna_text.strip()}", f"Masalah serius {dna_text.strip()}"],
            }
        }
    return universe


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
def enrich_story(sub, base_title, base_body, variant):
    angles=[
        ("orang biasa yang sedang bertahan","kebutuhan datang bersamaan","hidup seperti sengaja menguji saldo","tetap jalan meski keadaan absurd"),
        ("pekerja yang kelihatan baik-baik saja","tekanan pekerjaan bertemu masalah rumah","senyum harus lembur juga","manusia bukan mesin"),
        ("kepala keluarga yang menghitung kebutuhan","penghasilan harus dibagi ke banyak kebutuhan","uang punya banyak alamat sebelum masuk rekening","keluarga membuat kita terus berjuang"),
        ("anak muda yang ingin hidup mandiri","keinginan hidup layak berhadapan dengan biaya nyata","dewasa ternyata paket lengkap tanpa buku petunjuk","mandiri bukan berarti tidak boleh lelah"),
        ("seseorang yang mencoba terlihat normal","masalah pribadi disembunyikan di balik rutinitas","status online tidak berarti hidup baik-baik saja","tidak apa-apa mengakui lelah"),
        ("orang yang selalu berkata aman","kenyataan ternyata lebih berat dari ucapan","kata aman kadang cuma helm untuk hati","jujur pada diri sendiri adalah kekuatan"),
        ("seseorang yang berharap bulan depan lebih ringan","masalah lama belum selesai ketika masalah baru datang","bulan berganti, tagihan ikut naik kelas","harapan membuat kita tetap bergerak"),
        ("manusia yang mencoba mencari jalan keluar","solusi sementara bisa membawa konsekuensi baru","jalan pintas kadang punya gerbang tol","pilihan harus dipikirkan"),
        ("seseorang yang membandingkan hidupnya dengan orang lain","gengsi bertemu kenyataan","feed orang lain tidak menyertakan cicilannya","ukur hidup dengan perjalanan sendiri"),
        ("orang yang akhirnya menertawakan nasibnya sendiri","masalah tidak langsung hilang","kalau tidak bisa mengubah hari ini, jangan kasih masalah panggung sendirian","tetap punya humor dan harapan")]
    emotions=["relatable","tertekan tapi lucu","hangat dan getir","cemas namun optimistis","satir","emosional","rebel","ironis","reflektif","uplifting"]
    punchlines=[
        "Masalahnya serius. Tapi kalau ditangisi terus, saldo juga tidak bertambah.",
        "Di dunia kerja, bahkan senyum kadang punya target.",
        "Uang memang kecil, tetapi kebutuhan punya keluarga besar.",
        "Dewasa ternyata tidak ada tombol skip tutorial.",
        "Di layar terlihat normal. Di kepala sedang rapat darurat.",
        "Aman katanya. Yang tidak aman justru saldo dan pikiran.",
        "Tanggal berubah, perjuangan masih memakai seragam yang sama.",
        "Solusi cepat kadang datang membawa teman bernama konsekuensi.",
        "Orang lain upload hasilnya; kita tidak pernah melihat tagihannya.",
        "Kalau hidup sudah GOKIL, jangan biarkan humor ikut pensiun."]
    character,conflict,gokil,message=angles[(variant-1)%10]
    punch=punchlines[(variant-1)%10]; emotion=emotions[(variant-1)%10]
    body=f"{base_body} {character.capitalize()} menghadapi konflik: {conflict}. Sudut pandang GOKIL: {gokil}. Punchline: {punch} Pesan: {message}."
    return {"title":base_title,"body":body,"conflict":conflict,"gokil_angle":gokil,"punchline":punch,"emotion":emotion,"message":message}

def build_ten_stories(sub, universe=None):
    seeds=STORIES.get(sub,[])
    result=[enrich_story(sub,t,b,i) for i,(t,b) in enumerate(seeds[:3],1)]
    universe_name = universe["name"] if universe else "🌍 Realita Kehidupan di Bumi"
    context = universe["description"] if universe else "Realita kehidupan manusia sehari-hari."
    titles=[
        f"{sub.upper()} — SISI YANG TIDAK KELIHATAN",
        f"{sub.upper()} — HIDUP TIDAK PAKAI MANUAL",
        f"{sub.upper()} — SENYUM DULU, PIKIR NANTI",
        f"{sub.upper()} — MASALAH DATANG BERROMBONGAN",
        f"{sub.upper()} — ORANG BIASA, CERITA LUAR BIASA",
        f"{sub.upper()} — BESOK KITA COBA LAGI",
        f"{sub.upper()} — SERIUS, TAPI GOKIL"
    ]
    bodies=[
        f"Dalam universe {universe_name}, {sub.lower()} menjadi bagian dari cerita manusia. {context}",
        f"Ketika menghadapi {sub.lower()}, tokoh utama berharap ada buku panduan. Sayangnya kehidupan di {universe_name.lower()} hanya memberi tombol lanjut dan menyuruh manusia belajar sambil jalan.",
        f"Di tengah {sub.lower()}, tokoh utama memilih menertawakan ironi kecil yang muncul setiap hari agar masalah tidak terasa menjadi satu-satunya suara.",
        f"Masalah {sub.lower()} datang bukan sendirian. Satu selesai, dua menunggu. Tokoh utama akhirnya sadar bahwa hidup jarang membuat antrean secara tertib.",
        f"Seorang manusia biasa menjalani {sub.lower()} tanpa panggung besar. Justru dari rutinitas kecil itu terlihat perjuangan yang sering tidak masuk berita.",
        f"Setelah melewati hari yang berat karena {sub.lower()}, tokoh utama tidak menemukan solusi ajaib. Ia hanya menemukan keberanian untuk mencoba lagi besok.",
        f"{sub} memang serius, tetapi ada ironi yang terlalu lucu untuk tidak diceritakan. Tokoh utama memilih tertawa tanpa menghilangkan makna masalahnya."
    ]
    for j in range(7):
        idx = len(result) + 1
        result.append(enrich_story(sub, titles[j], bodies[j], idx))
    while len(result) < 10:
        idx = len(result) + 1
        result.append(enrich_story(sub, f"{sub.upper()} — CERITA KE-{idx}", f"Kehidupan dalam {universe_name} terus berjalan dan {sub.lower()} menjadi bagian dari perjuangan sehari-hari.", idx))
    return result[:10]

def generic_stories(sub, universe=None):
    return build_ten_stories(sub, universe)

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
    # Built with a list instead of a triple-quoted string so copy/paste into GitHub
    # cannot accidentally break the lyric string.
    lines = [
        "[Intro — Overture & Audio Hook 0:00–0:05]",
        "[Direct shout + strong guitar + kendang]",
        f"HEY! {title.upper()}!",
        "",
        "[Verse 1 — 0:05–0:30]",
        story,
        "Kita jalan, kita tahan",
        "Meski hidup kadang kelewatan",
        "",
        "[Pre-Chorus — 0:30–0:45]",
        "Kalau berat, jangan hilang",
        "Tarik napas, tetap berjuang",
        "Kita manusia, bukan mesin",
        "Masih berdiri, masih yakin",
        "",
        "[Chorus / Main Hook — starts by 0:45]",
        "HIDUP SERIUS, TAPI GOKIL!",
        "Masalah datang, kita senyum kecil",
        "HIDUP SERIUS, TAPI GOKIL!",
        "Jatuh sekali, bangkit lagi!",
        "",
        "[Verse 2]",
        "Tagihan datang, deadline mengejar",
        "Kepala panas, tetap sadar",
        "Dunia kadang tidak masuk akal",
        "Kita tertawa biar tidak tinggal",
        "",
        "[Bridge — Mystical]",
        "[Gamelan + suling bambu + ruang vokal]",
        "Di balik tawa ada cerita",
        "Di balik keras ada manusia",
        "We keep moving, we keep fighting",
        "Still alive, still surviving",
        "",
        "[Final Chorus]",
        "HIDUP SERIUS, TAPI GOKIL!",
        "Masalah datang, kita senyum kecil",
        "HIDUP SERIUS, TAPI GOKIL!",
        "Belum selesai — GAS LAGI!",
        "",
        "[Outro & Retention Loop]",
        "[Instrumental hit]",
        "Serius...",
        "tapi GOKIL...",
        f"{title.upper()}...",
        "GASS LAGI!"
    ]
    return "\n".join(lines)

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
    st.write("Setiap perubahan DNA mengubah universe, kategori, dan sub-tema. Setiap sub-tema menghasilkan 10 cerita berbeda dengan konflik, GOKIL angle, punchline, emosi, dan pesan.")

    dna = st.text_input("DNA Utama", DNA)
    universe = get_dynamic_categories(dna)
    st.success(f"🧬 Universe aktif: {universe['name']}")
    st.caption(universe["description"])
    category = st.selectbox("Kategori Realita — otomatis mengikuti DNA", list(universe["categories"].keys()))
    subtheme = st.selectbox("Sub-Tema Spesifik — otomatis mengikuti kategori", universe["categories"][category])
    custom_subtheme = st.text_input("Sub-tema custom (opsional)")
    chosen_subtheme = custom_subtheme.strip() or subtheme

    if st.button("🔥 GENERATE CERITA GOKIL", use_container_width=True):
        st.session_state.stories = build_ten_stories(chosen_subtheme, universe)
        st.session_state.story_index = 0
        st.session_state.final_title = ""
        st.session_state.titles = []
        st.session_state.dna = dna
        st.session_state.universe = universe["name"]
        st.session_state.category = category
        st.session_state.subtheme = chosen_subtheme

    if st.session_state.stories:
        st.success(
            f"🔥 {len(st.session_state.stories)} cerita siap | "
            f"DNA: {st.session_state.get('dna', DNA)} | "
            f"Universe: {st.session_state.get('universe', universe['name'])} | "
            f"Kategori: {st.session_state.get('category', category)} | "
            f"Sub-tema: {st.session_state.get('subtheme', chosen_subtheme)} | "
            f"GOKIL Level: {gokil_level}"
        )

        for i, story in enumerate(st.session_state.stories):
            with st.container(border=True):
                st.markdown(f"### {i+1:02d}. {story['title']}")
                st.write(story["body"])
                st.caption(f"🎯 Konflik: {story['conflict']}  |  🤣 GOKIL: {story['gokil_angle']}")
                st.caption(f"💥 Punchline: {story['punchline']}  |  ❤️ Emosi: {story['emotion']}  |  🧠 Pesan: {story['message']}")
                if st.button(f"👉 PILIH CERITA {i+1:02d}", key=f"story_{i}"):
                    st.session_state.story_index=i
                    st.session_state.final_title=""
                    st.session_state.titles=[]
        selected=st.session_state.stories[st.session_state.story_index]
        st.session_state.story_title=selected["title"]
        st.session_state.story_body=selected["body"]
        st.success(f"✅ Cerita aktif: {selected['title']}")

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
st.caption("3D GOKIL AI Music Factory V1.4 • Dynamic DNA → Category → Sub-Theme → 10 Stories → Title")
