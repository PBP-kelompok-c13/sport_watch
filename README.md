# ⚽ SportWatch

> Your all-in-one portal for sports news, live scores, and merchandise.

[![Deployment](https://img.shields.io/badge/Deployment-Live-brightgreen.svg)](https://faiz-yusuf-sportwatch.pbp.cs.ui.ac.id/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-darkgreen.svg)](https://www.djangoproject.com/)

---

## 📖 Daftar Isi
- [Tentang Aplikasi](#-tentang-aplikasi)
- [Fitur Utama](#-fitur-utama)
- [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
- [Peran Pengguna](#-peran-pengguna)
- [Cara Menjalankan Proyek](#-cara-menjalankan-proyek)
- [Tim Pengembang & Pembagian Tugas](#-tim-pengembang--pembagian-tugas)
- [Sumber Data Awal](#-sumber-data-awal)

---

## ⚽ Tentang Aplikasi — *SportWatch: Lebih dari Sekadar Portal Olahraga*

**SportWatch** adalah platform digital terpadu yang membawa dunia olahraga langsung ke tangan Anda. Tidak hanya sekadar membaca berita, pengguna dapat **merasakan atmosfer pertandingan secara real-time**, berdiskusi dengan sesama penggemar, hingga menjelajahi **produk dan merchandise resmi dari tim favorit mereka** semuanya dalam satu tempat.

Kami percaya bahwa olahraga bukan hanya tentang skor dan statistik, tetapi juga **tentang emosi, komunitas, dan gaya hidup**. Karena itu, SportWatch hadir untuk menjadi jembatan antara penggemar dan dunia olahraga global dengan cara yang informatif, interaktif, dan inspiratif.

---

### 🎯 Visi

Menjadi **portal olahraga digital paling interaktif di Indonesia**, yang menghubungkan penggemar, berita, dan brand olahraga dalam satu ekosistem yang dinamis.

### 💡 Misi

1. Menyediakan **berita olahraga terkini** dari berbagai sumber terpercaya dalam tampilan yang modern dan mudah diakses.
2. Menghadirkan **Live Scoreboard** yang akurat dan update agar pengguna tak pernah ketinggalan momen penting.
3. Mengembangkan ruang interaksi antar-fans melalui fitur **komentar dan diskusi berita**.
4. Memberikan pengalaman berbelanja **merchandise eksklusif dan produk olahraga** tanpa harus berpindah platform.

---

### 🌟 Nilai Unggulan SportWatch

* **Semua olahraga, satu portal:** Dari sepak bola hingga basket, pengguna dapat mengikuti beragam cabang olahraga dalam satu tempat.
* **Interaktif & Sosial:** Fans bisa saling berdiskusi, memberi opini, atau berbagi antusiasme lewat fitur komentar berita.
* **Personalized Experience:** Sistem akan terus dikembangkan untuk menampilkan berita dan produk sesuai minat pengguna.
* **Marketplace Olahraga:** Pengguna bisa langsung membeli perlengkapan olahraga atau merchandise favorit melalui fitur *Shop*.
* **Up-to-date Scores:** Pantau skor pertandingan secara langsung, baik melalui update manual maupun integrasi API ke depan.

---

### 🚀 Mengapa SportWatch Layak Diperhatikan

Bagi pengguna, **SportWatch** menghadirkan pengalaman olahraga yang lebih dekat, praktis, dan menyenangkan.
Bagi investor atau mitra, platform ini membuka peluang besar dalam **pasar digital sporttainment** yang terus tumbuh, dengan potensi monetisasi dari iklan, afiliasi merchandise, dan sistem langganan berita premium.

SportWatch bukan hanya portal berita—**ini adalah ekosistem olahraga digital masa depan.**


---

## ✨ Fitur Utama
- **📰 Portal Berita**: Menampilkan berita olahraga terkini dengan format yang rapi dan mudah dibaca.
- **Live Scoreboard**: Memantau dan menampilkan skor pertandingan secara langsung.
- **🛒 Fitur Belanja (Shop)**: Halaman khusus untuk melihat dan membeli merchandise olahraga.

## Fitur tambahan 
- Fans bisa melihat suatu bertia terus bisa reply dan saling chatting mengenai 1 berita tersebut
- Upcoming jadwal pertandingan yang hits, 

---

## 🛠️ Teknologi yang Digunakan
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (Development)
- **Deployment**: Platform As A Service (PWS)

---

## 👤 Peran Pengguna
Aplikasi ini dirancang untuk melayani berbagai jenis pengguna:
- **User**: Pengguna umum website yang dapat mengakses informasi seputar olahraga, memantau berita atau perkembangan tim/klub, serta melakukan aktivitas seperti melihat dan membeli produk olahraga maupun merchandise.
- **Guest** : Pengunjung yang dapat membaca berita dan melihat skor atau produk, tetapi belum dapat berinteraksi atau bertransaksi sebelum mendaftar.
- **Admin**: Pengguna dengan hak istimewa untuk mengatur konten dan fungsionalitas website.

---

## 🚀 Cara Menjalankan Proyek

### 1. Clone Repositori
```bash
git clone https://github.com/<your-username>/sport-watch.git
cd sport-watch
```

### 2. Buat dan Aktifkan Virtual Environment
```bash
# Windows
python -m venv env
.\env\Scripts\activate

# Linux / macOS
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Migrasi Database
```bash
python manage.py migrate
```

### 5. Jalankan Development Server
```bash
python manage.py runserver
```
Buka browser dan kunjungi `http://127.0.0.1:8000`

---

## 👨‍💻 Tim Pengembang & Pembagian Tugas

### Anggota Kelompok:
1.  **Faiz Yusuf Ridwan** - `2406434292`
2.  **Muhammad Fadhil Al Afifi Fajar** - `2406430104`
3.  **Edward Jeremy Worang** - `2406359475`
4.  **Kadek Ngurah Septyawan Chandra Diputra** - `2406420772`
5.  **Dzaki Abrar Fatihul Ihsan** - `2306275241`



## 📑 Pembagian Tugas Modul (Breakdown):

### 1. **Portal Berita (`portal-berita`)**

**Penanggung jawab:** Faiz Yusuf Ridwan

**Deskripsi Modul:** Menyediakan halaman berita olahraga terkini, CRUD berita oleh admin, dan filter berita berdasarkan kategori.

**Sub-tugas:**
* **Backend:**

  * Model berita (judul, isi, tanggal, kategori).
  * View untuk daftar berita & detail berita.
  * Admin interface untuk tambah/ubah/hapus berita.
  * Menandai berita trending / top news.
* **Frontend:**

  * Template halaman daftar berita.
  * Template halaman detail berita.
  * Layout yang responsif & mudah dibaca.

---

### 2. **Scoreboard (`scoreboard`)**

**Penanggung jawab:** Muhammad Fadhil Al Afifi Fajar

**Deskripsi Modul:** Menampilkan skor pertandingan olahraga secara real-time atau update manual.

**Sub-tugas:**

* **Backend:**

  * Model pertandingan (tim A, tim B, skor, waktu).
  * API endpoint untuk update skor (opsional).
* **Frontend:**

  * Widget scoreboard di halaman utama.
  * Tampilan skor yang mudah di-scan pengguna.

  Arahan atau referensi CRUD Scoreboard bisa ikuti seperti ini:
  Create:
  Admin dapat menambahkan pertandingan baru ke scoreboard (contoh: Timnas Indonesia vs Jepang, tanggal 10 Oktober 2025).

  Read:
  Pengguna dapat melihat daftar pertandingan beserta skor terkini.

  Update:
  Admin dapat memperbarui skor pertandingan saat berlangsung (misalnya: menit ke-60 skor berubah jadi 2–1). (untuk olahraga seperti permainan basket dimana poinnya kecetak terus, kayaknya harus pake semacam AI atau API google 😅)

  Delete:
  Admin dapat menghapus data pertandingan (misalnya pertandingan uji coba yang batal dilaksanakan)

---

### 3. **Fitur pencarian**

**Penanggung jawab:** Kadek Ngurah Septyawan Chandra Diputra

**Deskripsi Modul:** Menambahkan fitur ekstra untuk meningkatkan UX di portal berita.

**Sub-tugas:**


* Filter & pencarian berita.
* Filter dan pencarian product
* Halaman pencarian dan hasil pencarian
* Pencarian apa saja
* Sudah termasuk frontend dan backend (mungkin)



---
### 4. **Shop (`shop`)**

**Penanggung jawab:** Edward Jeremy Worang

**Deskripsi Modul:** Halaman khusus untuk melihat dan membeli merchandise olahraga.

**Sub-tugas:**

* **Backend:**

  * Model produk (nama, harga, stok, kategori, review).
  * Filtering dan rating system.
* **Frontend:**

  * Template daftar produk (grid view).
  * Template detail produk.

---

### 5. **Fitur Belanja (`fitur-belanja`)**

**Penanggung jawab:** Dzaki Abrar Fatihul Ihsan

**Deskripsi Modul:** Mengatur logika pembelian & checkout.

**Sub-tugas:**

* Tambah produk ke keranjang.
* Hapus produk dari keranjang.
* Hitung total harga.
* Simulasi checkout (dummy payment).
* Halaman checkout.
---

**Link Figma:**
https://exit-upload-30788858.figma.site/ (Reference)

---
## 📚 Sumber Data Awal
- [Detik Sport](https://sport.detik.com/) untuk module Portal Berita
- [Kompas Olahraga](https://olahraga.kompas.com/) untuk module Portal Berita
- [ESPN] (https://global.espn.com/)  untuk module Scoreboard
- [Decathlon] (https://www.decathlon.co.id/en-ID/c/team-sports.html?srsltid=AfmBOopfZCShVKLqiBjDRFXVJD3X64eG61l3b8Zr80wmR0s69gVibtYt) untuk module Shop
- [SportsStation] (https://www.sportsstation.id/) untuk Module Shop
- [FootLocker] (https://www.footlocker.id/nike.html) untuk Module Shop
