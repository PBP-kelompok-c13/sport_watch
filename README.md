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

## 📌 Tentang Aplikasi
**SportWatch** adalah portal berita yang menyajikan informasi terbaru dari dunia olahraga. Pengguna dapat mengakses *Live Scoreboard*, mengecek berita terkini, dan melihat produk-produk baru melalui fitur *Shop*.

---

## ✨ Fitur Utama
- **📰 Portal Berita**: Menampilkan berita olahraga terkini dengan format yang rapi dan mudah dibaca.
- ** scoreboard Live Scoreboard**: Memantau dan menampilkan skor pertandingan secara langsung.
- **🛒 Fitur Belanja (Shop)**: Halaman khusus untuk melihat dan membeli merchandise olahraga.

## Fitur tambahan (Opsional jika fitur utama sudah aman)
- Fans bisa melihat suatu bertia terus bisa reply dan saling chatting mengenai 1 berita tersebut
- Upcoming jadwal pertandingan yang hits, 
- Dan lain-lain kalau modulenya tidak cukup atau tidak sesuai definisi "module"

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

---

### 3. **Fitur Berita Tambahan (`fitur-berita`)**

**Penanggung jawab:** Kadek Ngurah Septyawan Chandra Diputra
**Deskripsi Modul:** Menambahkan fitur ekstra untuk meningkatkan UX di portal berita.
**Sub-tugas:**

* Filter & pencarian berita.
* Menandai berita trending / top news.
* Pagination atau infinite scroll.

---
### 4. **Shop (`shop`)**

**Penanggung jawab:** Dzaki Abrar Fatihul Ihsan
**Deskripsi Modul:** Halaman khusus untuk melihat dan membeli merchandise olahraga.
**Sub-tugas:**

* **Backend:**

  * Model produk (nama, harga, stok, kategori).
  * Model transaksi / keranjang belanja.
* **Frontend:**

  * Template daftar produk (grid view).
  * Template detail produk.

---

### 5. **Fitur Belanja (`fitur-belanja`)**

**Penanggung jawab:** Edward Jeremy Worang
**Deskripsi Modul:** Mengatur logika pembelian & checkout.
**Sub-tugas:**

* Tambah produk ke keranjang.
* Hapus produk dari keranjang.
* Hitung total harga.
* Simulasi checkout (dummy payment).

---
## 📚 Sumber Data Awal
- [Detik Sport](https://sport.detik.com/)
- [Kompas Olahraga](https://olahraga.kompas.com/)
