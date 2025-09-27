# ⚽ SportWatch

> Your all-in-one portal for sports news, live scores, and merchandise.

[![Deployment](https://img.shields.io/badge/Deployment-Live-brightgreen.svg)](https://pbp.cs.ui.ac.id/web/project/faiz.yusuf/sportwatch)
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

---

## 🛠️ Teknologi yang Digunakan
- **Backend**: Python, Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (Development)
- **Deployment**: Platform As A Service (PWS)

---

## 👤 Peran Pengguna
Aplikasi ini dirancang untuk melayani berbagai jenis pengguna:
- **Guest User**: Pengguna umum yang hanya ingin melihat informasi di halaman awal.
- **Sports Fans**: Pengguna yang setia pada satu tim/klub dan aktif memantau berita terkait.
- **Shopper**: Pengguna yang tertarik pada dunia olahraga dan memiliki daya beli untuk alat-alat olahraga atau fan merchandise.
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

### Pembagian Tugas Modul:
- **`portal-berita`** (Faiz Yusuf Ridwan)
  - Mengatur tampilan dan format berita.
  - **`scoreboard`** (Muhammad Fadhil Al Afifi Fajar): Mengawasi scoreboard di halaman awal.
  - **`fitur-berita`** (Kadek Ngurah S. C. D.): Mengatur penampilan berita di halaman awal.
- **`shop`** (Dzaki Abrar Fatihul Ihsan)
  - Mengatur halaman belanja.
  - **`fitur-belanja`** (Edward Jeremy Worang): Mengatur fungsionalitas berbelanja.

---

## 📚 Sumber Data Awal
- [Detik Sport](https://sport.detik.com/)
- [Kompas Olahraga](https://olahraga.kompas.com/)
