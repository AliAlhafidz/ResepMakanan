# 🍳 Dapur Nusa

> Website resep masakan nusantara berbasis DATH Stack — **Django + Alpine.js + Tailwind CSS + HTMX** — dengan arsitektur HTML-over-the-Wire dan tampilan Material Design 3.

---

## 🚀 Fitur Utama

- **Auth & Role**: Daftar, login, logout, profil pengguna; role Admin dan Pengguna
- **Jelajah & Cari**: Filter berdasarkan kategori, bahan, waktu masak, dan tingkat kesulitan
- **Detail Resep**: Info waktu/porsi/kesulitan, bahan dengan jumlah porsi dinamis, langkah, catatan, estimasi gizi, resep terkait
- **Favorit**: Simpan resep favorit dengan toggle real-time via HTMX
- **Daftar Belanja**: Tambah bahan ke daftar belanja, centang/hapus item
- **Moderasi Admin**: Setujui atau tolak resep komunitas, dashboard statistik

---

## 🛠 Stack Teknologi

| Komponen | Teknologi |
|---|---|
| Backend | Django 5.2 (Python 3.14) |
| Frontend reaktif | Alpine.js 3.x |
| CSS utility | Tailwind CSS (Play CDN) |
| Interaktivitas | HTMX 2.x |
| Database | SQLite (development) |
| Gambar | Pillow 12.x |

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python 3.11+ (diuji di Python 3.14.6)
- pip

### Langkah-langkah

```bash
# 1. Clone repositori
git clone <url-repo> dapur-nusa
cd dapur-nusa

# 2. Buat & aktifkan virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate.bat     # Windows

# 3. Install dependensi
pip install -r requirements.txt

# 4. Konfigurasi lingkungan
cp .env.example .env
# Edit .env sesuai kebutuhan (minimal: SECRET_KEY)

# 5. Jalankan migrasi
python manage.py migrate

# 6. (Opsional) Isi data contoh
python manage.py seed_data

# 7. Buat akun superuser
python manage.py createsuperuser

# 8. Jalankan server development
python manage.py runserver
```

Buka browser di **http://localhost:8000**

---

## 👤 Akun Demo (setelah menjalankan `seed_data`)

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Pengguna | `budi_santoso` | `budi123` |

---

## 🗂 Struktur Proyek

```
dapur-nusa/
├── accounts/          # Auth, profil, sinyal
│   ├── migrations/
│   ├── models.py      # User (AbstractUser + role), UserProfile
│   ├── views.py       # Login, register, logout, profil
│   ├── forms.py       # Form auth dengan styling Material Design 3
│   └── signals.py     # Auto-buat UserProfile saat User baru dibuat
├── config/            # Konfigurasi proyek Django
│   ├── settings.py
│   └── urls.py
├── recipes/           # App utama resep
│   ├── management/commands/seed_data.py  # Data contoh
│   ├── migrations/
│   ├── models.py      # Recipe, Ingredient, InstructionStep, dll.
│   ├── views.py       # Semua view resep
│   ├── forms.py       # Form resep + formset bahan/langkah
│   └── urls.py
├── static/
│   ├── js/            # htmx.min.js, alpine.min.js (lokal)
│   └── src/input.css  # Input CSS untuk Tailwind build pipeline
├── templates/
│   ├── base.html      # Layout utama + drawer mobile + navbar
│   ├── accounts/      # Login, register, profil
│   └── recipes/       # Home, list, detail, form, dashboard, dll.
├── .env.example
├── .gitignore
├── requirements.txt
└── manage.py
```

---

## 🧪 Tes

```bash
python manage.py test --verbosity=2
```

---

## 🔒 Keamanan Production

Sebelum deploy ke production:

1. Set `DEBUG=False` di `.env`
2. Generate `SECRET_KEY` baru yang kuat
3. Set `ALLOWED_HOSTS` ke domain produksi
4. Jalankan `python manage.py check --deploy` dan perbaiki semua peringatan
5. Gunakan HTTPS dan set `SECURE_SSL_REDIRECT=True`
6. Jalankan `python manage.py collectstatic`

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan pembelajaran. Resep dan konten adalah milik kontributornya.
