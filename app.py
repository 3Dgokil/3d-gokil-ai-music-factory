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
st.caption("🔥 V1.3 FINAL — 10 STORY ENGINE AKTIF")
st.success("🔥 V1.3 — 10 STORY ENGINE AKTIF")

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

def build_ten_stories(sub):
    seeds=STORIES.get(sub,[])
    result=[enrich_story(sub,t,b,i) for i,(t,b) in enumerate(seeds[:3],1)]
    titles=[f"{sub.upper()} — REKENING DAN REALITA",f"{sub.upper()} — HIDUP TIDAK PAKAI MANUAL",f"{sub.upper()} — SENYUM DULU, PIKIR NANTI",f"{sub.upper()} — MASALAH DATANG BERROMBONGAN",f"{sub.upper()} — ORANG BIASA, CERITA LUAR BIASA",f"{sub.upper()} — BESOK KITA COBA LAGI",f"{sub.upper()} — SERIUS, TAPI GOKIL"]
    bodies=[f"Realita {sub.lower()} membuat seseorang harus membagi tenaga, waktu, dan pikiran. Tidak ada yang benar-benar gratis, bahkan ketenangan kadang harus diperjuangkan.",f"Ketika menghadapi {sub.lower()}, seseorang berharap ada buku panduan. Sayangnya kehidupan hanya memberi tombol lanjut dan menyuruh manusia belajar sambil jalan.",f"Di tengah {sub.lower()}, tokoh utama memilih menertawakan ironi kecil yang muncul setiap hari agar masalah tidak terasa menjadi satu-satunya suara.",f"Masalah {sub.lower()} datang bukan sendirian. Satu selesai, dua menunggu. Tokoh utama akhirnya sadar bahwa hidup memang jarang membuat antrean secara tertib.",f"Seorang manusia biasa menjalani {sub.lower()} tanpa panggung besar. Justru dari rutinitas kecil itu terlihat perjuangan yang sering tidak masuk berita.",f"Setelah melewati hari yang berat karena {sub.lower()}, tokoh utama tidak menemukan solusi ajaib. Ia hanya menemukan keberanian untuk mencoba lagi besok.",f"{sub} memang serius, tetapi ada ironi yang terlalu lucu untuk tidak diceritakan. Tokoh utama memilih tertawa tanpa menghilangkan makna masalahnya."]
    for j in range(7):
        idx = len(result) + 1
        result.append(enrich_story(sub, titles[j], bodies[j], idx))
    while len(result) < 10:
        idx = len(result) + 1
        result.append(enrich_story(
            sub,
            f"{sub.upper()} — CERITA KE-{idx}",
            f"Kehidupan nyata terus berjalan dan {sub.lower()} menjadi bagian dari perjuangan sehari-hari.",
            idx
        ))
    return result[:10]

def generic_stories(sub):
    return build_ten_stories(sub)

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
        "Kita manus
