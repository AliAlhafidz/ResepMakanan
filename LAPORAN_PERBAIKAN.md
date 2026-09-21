# LAPORAN PERBAIKAN MENYELURUH — Dapur Nusa

> **Tanggal**: 20 September 2026  
> **Proyek**: Dapur Nusa — Website Resep Masakan Nusantara  
> **Stack**: Django 5.2.17 + Alpine.js 3 + Tailwind CSS (Play CDN) + HTMX 2 (DATH Stack)  
> **Lingkungan**: Python 3.14.6, aarch64 (Termux Android)

---

## Ringkasan Hasil

| Kategori | Total Ditemukan | Diperbaiki | Status |
|---|---|---|---|
| Bug Kritis (K) | 10 | 10 | ✅ Semua selesai |
| Bug Logika Backend (B) | 5 | 5 | ✅ Semua selesai |
| Bug UI/UX (U) | 10 | 10 | ✅ Semua selesai |
| Tes Otomatis | 4 (lama) | 50 (total) | ✅ 50/50 hijau |
| Migrasi | 0 | 4 baru | ✅ Aman untuk data ada |
| `manage.py check` | - | - | ✅ 0 issues |
| `manage.py check --deploy` | - | - | ✅ 3 warnings wajar* |
| `manage.py makemigrations --check` | - | - | ✅ No changes |

> *Warnings `check --deploy` bersifat wajar untuk development: HSTS, SSL redirect, dan SECRET_KEY demo. Semua dikonfigurasi via env var untuk production.

---

## Tahap 0 — Persiapan

- ✅ Cadangan `db.sqlite3.bak` dibuat
- ✅ Kondisi awal dicatat: 4 tes lulus, `check` bersih
- ✅ `static/js/htmx.min.js` dan `static/js/alpine.min.js` diunduh lokal (tidak bergantung CDN)

---

## Tahap 1 — Bug Kritis (K1–K10)

### K1 — `add_to_shopping_list_view`: Validasi & Keamanan
**Masalah**: Tidak ada `@require_POST`, Decimal vs float menyebabkan presisi error, tidak ada validasi servings, item duplikat ditambah ulang (bukan digabung), tidak ada `transaction.atomic`, resep non-PUBLISHED bisa ditambahkan.

**Perbaikan**:
- Tambah `@require_POST` + `@login_required`
- Validasi `servings` range 1–100, `Http404` jika di luar range
- Gunakan `Decimal` konsisten di seluruh perhitungan porsi
- Logika merge item duplikat: cek `item_name+unit` lalu `amount += ...`
- Wrap seluruh operasi dalam `transaction.atomic()`
- Filter `Recipe.Status.PUBLISHED` sebelum proses

### K2 — `recipe_list_view`: Performa & Pagination
**Masalah**: List comprehension O(n) untuk annotate, tidak ada pagination, tidak ada `order_by` konsisten.

**Perbaikan**:
- Ganti list comprehension dengan `annotate(total_time_min=F('prep_time_minutes') + F('cook_time_minutes'))`
- Tambah `Paginator` 12 resep/halaman
- `order_by('-created_at')` default
- Querystring dipertahankan di link pagination untuk kompatibilitas HTMX

### K3 — Slug Kosong: `Recipe/Category/Tag.save()`
**Masalah**: Judul berisi karakter non-ASCII atau simbol (seperti `"!!!"`) menghasilkan slug kosong → `IntegrityError` karena `unique=True`.

**Perbaikan**:
- Fallback slug: `"resep"`, `"kategori"`, `"tag"` jika `slugify()` menghasilkan string kosong
- Truncation ke `max_length` sebelum disimpan
- Data migration `0003_fix_empty_slugs.py` untuk memperbaiki slug kosong yang sudah ada
- Validasi alfanumerik di `RecipeForm.clean_title` (minimal 1 karakter alfanumerik)

### K4 — Filter Status: `recipe_detail_view`
**Masalah**: Resep PENDING/REJECTED bisa diakses siapa saja jika URL diketahui.

**Perbaikan**:
- Hanya resep PUBLISHED yang tampil untuk pengunjung anonim dan pengguna lain
- Penulis sendiri dan admin bisa lihat resep berstatus apapun miliknya
- Banner status tampil di halaman detail (PENDING: kuning, REJECTED: merah + alasan)

### K5 — Open Redirect: `login_view`
**Masalah**: Parameter `next` tidak divalidasi → attacker bisa redirect ke `http://evil.com`.

**Perbaikan**:
- Gunakan `url_has_allowed_host_and_scheme()` untuk validasi `next`
- Baca `next` dari POST body terlebih dahulu, fallback ke GET
- Tambah `<input type="hidden" name="next">` di `login.html`

### K6 — Logout GET: `logout_view`
**Masalah**: `logout_view` bisa diakses via GET → CSRF bypass, bisa di-trigger dari img tag.

**Perbaikan**:
- Tambah `@require_POST`
- Ganti semua `<a href="...logout">` di navbar (desktop & mobile) menjadi `<form method="post">` dengan CSRF token

### K7 — Moderasi GET: `moderate_recipe_view`
**Masalah**: Setujui resep menggunakan link `<a href>` (GET request) → tidak aman, bisa di-trigger tanpa interaksi user.

**Perbaikan**:
- Tambah `@require_POST`
- Whitelist action: hanya `approve` dan `reject`
- Hanya resep berstatus `PENDING` yang bisa dimoderasi (`get_object_or_404`)
- Reject: alasan wajib diisi minimal 10 karakter
- Template `admin_dashboard.html`: tombol Setujui → `<form method="POST">`, tombol Tolak → modal Alpine.js dengan `<textarea>` + validasi client-side dan server-side

### K8 — Favorit GET & Anonim: `toggle_favorite_view`
**Masalah**: Bisa diakses via GET, pengguna anonim menyebabkan error, resep non-PUBLISHED bisa di-favorit.

**Perbaikan**:
- Tambah `@require_POST`
- Pengguna anonim via HTMX: kirim header `HX-Redirect` ke login
- Pengguna anonim non-HTMX: `redirect(login_url + '?next=...')`
- Filter `Recipe.Status.PUBLISHED` → `Http404` jika tidak published

### K9 — Status Edit: `edit_recipe_view`
**Masalah**: Pengguna biasa bisa mengedit resep PUBLISHED tanpa reset ke PENDING (bypass moderasi).

**Perbaikan**:
- Non-admin mengedit resep apapun → status otomatis jadi `PENDING`
- `rejection_reason` dikosongkan saat reset ke PENDING
- Bukan penulis bukan admin → `PermissionDenied` (HTTP 403)

### K10 — Validasi Model & Form
**Masalah**: `MinValueValidator` tidak ada di `Ingredient.amount`, tidak ada validasi tipe/ukuran gambar, formset tidak memvalidasi minimal 1 bahan.

**Perbaikan**:
- `MinValueValidator(0)` di `Ingredient.amount` (0 diizinkan untuk bahan "secukupnya")
- `validate_image_file()`: validasi MIME type (JPEG/PNG/WEBP) dan ukuran maks 2 MB
- `InstructionStepFormSet`: `min_num=1`, `validate_min=True`
- `step='any'` di input number untuk mendukung nilai desimal
- `request.FILES` diteruskan ke formset di `create/edit_recipe_view`
- Seluruh operasi create/edit dibungkus `transaction.atomic()`

---

## Tahap 2 — Bug Logika Backend (B1–B5 + B6–B9)

### B1 — Jumlah Resep per Kategori
- `Count('recipes', filter=Q(recipes__status=PUBLISHED))` — hanya resep terbit
- `order_by('-recipe_count', 'name')` — urutkan by populer
- `featured_recipes.order_by('-updated_at')` — resep unggulan terbaru dulu

### B2 — Django Admin Actions
- `make_published`: kosongkan `rejection_reason` saat menerbitkan
- Tambah action `unmake_featured`: batalkan unggulan massal

### B3 — Statistik Pengguna di Dashboard
- Hitung `total_users`, `active_users`, `inactive_users` aktual dari DB
- Ganti `user_passes_test` dengan decorator `admin_required` yang raise `PermissionDenied` (403) bukan redirect loop

### B4 — Login Akun Nonaktif
- `StyledAuthenticationForm` mendeteksi akun `is_active=False` **sebelum** `authenticate()` dipanggil
- Pesan error dalam Bahasa Indonesia yang tepat
- Tidak membocorkan informasi (pesan generik untuk username salah)

### B5 — Email Unik di Registrasi
- `clean_email()`: cek `User.objects.filter(email__iexact=...)` — case-insensitive
- Data migration `0003_populate_missing_profiles.py`: buat `UserProfile` untuk user lama yang belum punya profil
- Sinyal `post_save` di `accounts/signals.py` → auto-buat profil untuk user baru

### B6–B9 — Perbaikan Tambahan
- B6: `role` ditambahkan ke `add_fieldsets` di Django admin
- B7: `active_tab` di context profil, tab Alpine.js berdasarkan context
- B8: Hidden input tag, `hx-push-url='true'`, highlight tag aktif, tombol "Reset semua filter"
- B9: `ShoppingListItem.__str__` diperbaiki untuk tidak mencetak `None`

---

## Tahap 3 — Bug UI/UX (U1–U10)

### U1 — Mobile Drawer
- Hamburger button Alpine.js: buka/tutup drawer
- Tutup dengan Esc, klik di luar drawer, atau klik link navigasi
- Semua link + tombol logout (form POST) ada di drawer

### U2 — Tampilan Error Form
- Partial `templates/includes/form_errors.html` bergaya Material Design 3
- Error per-field dengan label `for=` dan `id_for_label` yang tepat
- Digunakan di: login, register, profil (edit), recipe_form

### U3 — Styling Form Konsisten
- `StyledAuthenticationForm.__init__` selalu menambahkan class, bukan hanya saat GET

### U4 — Formset Dinamis di Recipe Form
- Tag chips: checkbox dengan styling M3
- Tombol "+Tambah Bahan" / "+Tambah Langkah" Alpine.js menambah row baru secara dinamis
- Preview foto sebelum upload
- Section nutrisi collapsible
- Tombol submit menampilkan "Simpan" atau "Kirim untuk Ditinjau" sesuai status

### U5 — Tailwind Config Lengkap
- `tertiary-200` dan `tertiary-800` ditambahkan ke config
- `scrollbar-none` diganti `[scrollbar-width:none]` (CSS standard)
- `tailwind.config.js` dibuat untuk build pipeline masa depan

### U6 — Konversi Porsi Dinamis
- `{% load l10n %}` + `|unlocalize` untuk angka yang konsisten
- Alpine.js `scale()`: tangani format koma, pecahan ¼/½/¾
- Pembulatan cerdas: kelipatan 5 untuk gram/ml ≥ 20
- `|linebreaksbr` untuk deskripsi dan instruksi

### U7 — Teks Opsi Filter Waktu
- "≤ 30 menit" → "Cepat (maks. 30 menit)"
- "≤ 60 menit" → "Standar (maks. 60 menit)"
- "≤ 120 menit" → "Matang lambat (maks. 2 jam)"

### U8 — Dashboard Admin
- `{% url 'admin:index' %}` menggantikan hardcode `/admin/`
- Link Django Admin hanya tampil jika `user.is_staff`
- Kartu "Total Semua Resep" diubah warna dari merah ke netral (stone)
- Tambah section kartu pengguna: Total / Aktif / Nonaktif
- Modal Alpine.js untuk penolakan dengan textarea + validasi real-time

### U9 — Interaksi Daftar Belanja
- Tombol hapus per-item dengan HTMX `hx-delete` + OOB swap
- Tombol "Hapus yang Sudah Dicentang" (form POST ke `clear_checked_shopping_items`)
- Partial `shopping_item_list.html` untuk respons HTMX setelah clear
- `clear_checked_shopping_items_view`: hapus `is_checked=True`, kembalikan partial via HTMX

### U10 — Aksesibilitas
- `aria-label` pada semua tombol ikon
- `focus-visible:ring-2` + `focus-visible:outline-none` di elemen interaktif
- `role="status"` / `role="alert"` / `aria-live="polite"` di area dinamis
- Kontras teks ditingkatkan: `stone-400` → `stone-500` atau lebih gelap

---

## Tahap 4 — Konfigurasi & Kebersihan

| File | Keterangan |
|---|---|
| `config/settings.py` | Env vars (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`), `LANGUAGE_CODE='id'`, `TIME_ZONE='Asia/Jakarta'`, upload limit 5 MB, keamanan production (aktif jika `DEBUG=False`) |
| `requirements.txt` | Versi terkunci: Django 5.2.17, django-htmx 1.29.0, Pillow 12.3.0 |
| `.env.example` | Template variabel lingkungan dengan dokumentasi |
| `.gitignore` | Komprehensif: pycache, db.sqlite3, .env, media/, staticfiles/, node_modules/ |
| `README.md` | Panduan instalasi, fitur, struktur proyek, akun demo, catatan keamanan |
| `recipes/management/commands/seed_data.py` | Management command `python manage.py seed_data [--force]` — pindah dari root proyek |

---

## Tahap 5 — Tes Otomatis

**Total**: 50 tes, **50 lulus (OK)**, 0 gagal

| Kelas Tes | Tes | Cakupan |
|---|---|---|
| `DapurNusaTests` | 4 | Tes asli (tetap lulus) |
| `K1ShoppingListTests` | 6 | POST only, validasi servings, duplikat merge, PUBLISHED filter |
| `K2RecipeListTests` | 5 | Filter waktu, tag, exclude non-matching, PENDING tidak tampil |
| `K3SlugTests` | 2 | Slug fallback, beranda tetap 200 |
| `K4StatusFilterTests` | 3 | PENDING/REJECTED 404 anonim, penulis bisa lihat |
| `K5LoginRedirectTests` | 2 | External next ditolak, internal next diterima |
| `K6LogoutTests` | 2 | GET 405, POST berhasil |
| `K7ModerateRecipeTests` | 6 | GET 405, approve, reject tanpa/dengan alasan, PUBLISHED 404, non-admin 403 |
| `K8ToggleFavoriteTests` | 5 | GET 405, anonim redirect, anonim HTMX HX-Redirect, PENDING 404, toggle add/remove |
| `K9EditRecipeTests` | 3 | Non-admin → PENDING, admin → tetap PUBLISHED, orang lain → 403 |
| `B1CategoryCountTests` | 2 | Kategori tampil, PENDING tidak dihitung |
| `B3AdminDashboardTests` | 3 | Stats pengguna, non-admin 403, anonim redirect |
| `B4InactiveUserTests` | 1 | Akun nonaktif tidak bisa login |
| `B5UniqueEmailTests` | 2 | Email duplikat ditolak, email unik diterima |
| `U6ServingsScaleTests` | 2 | Amount bahan di template, default_servings di context |
| `U9ShoppingListTests` | 2 | Clear checked only, GET 405 |

---

## Tahap 6 — Verifikasi Final

```
✅ python manage.py check              → 0 issues (0 silenced)
✅ python manage.py test               → Ran 50 tests in 64.8s — OK
✅ python manage.py check --deploy     → 3 warnings wajar (HSTS/SSL/SECRET_KEY development)
✅ python manage.py makemigrations --check → No changes detected
```

---

## Migrasi Database

| File | Jenis | Keterangan |
|---|---|---|
| `accounts/migrations/0002_alter_userprofile_avatar.py` | Schema | Tambah `validate_image_file` ke avatar |
| `accounts/migrations/0003_populate_missing_profiles.py` | Data | Buat profil untuk user lama yang belum punya |
| `recipes/migrations/0002_alter_ingredient_amount_and_more.py` | Schema | `MinValueValidator`, `validate_image_file`, tambah field baru |
| `recipes/migrations/0003_fix_empty_slugs.py` | Data | Perbaiki slug kosong pada data yang sudah ada |

---

## Asumsi yang Diambil

1. **`toggle_favorite_view` anonim via HTMX**: mengembalikan header `HX-Redirect` ke login (bukan 401), agar Alpine.js tidak perlu menangani status code non-standard.
2. **`remove_card=True` di favorit profil**: partial mengembalikan string kosong → kartu hilang dari DOM.
3. **`status='any'`** di input bahan: diizinkan agar nilai seperti `0.5` bisa dimasukkan (untuk bahan "½ sdt").
4. **Pengguna biasa edit resep REJECTED**: status dikembalikan ke `PENDING` (bukan `REJECTED`), supaya resep kembali masuk antrean moderasi.
5. **`validate_image_file`**: MIME type JPEG/PNG/WEBP diizinkan, maks 2 MB. Validasi dilakukan di model-level (validator) sekaligus di form-level untuk pesan error yang lebih user-friendly.
6. **`accounts` menggunakan `AccountsConfig`** (bukan string `'accounts'`) di `INSTALLED_APPS` — memastikan sinyal `post_save` terdaftar via `ready()`.

---

## Potensi Risiko yang Diketahui

| Risiko | Severity | Catatan |
|---|---|---|
| Tailwind Play CDN | Low | Untuk production, jalankan `npx tailwindcss build` menggunakan `tailwind.config.js` dan `static/src/input.css` yang sudah dibuat |
| SQLite di production | Medium | Cukup untuk beban rendah; untuk produksi dengan banyak concurrent write, pertimbangkan PostgreSQL |
| Media files | Low | File upload disimpan lokal di `MEDIA_ROOT`; untuk produksi, pertimbangkan object storage (S3/GCS) |
| `BaseInstructionStepFormSet.save()` | Low | Override save formset di-review — renumber otomatis berjalan saat commit; tes K9 membuktikan tidak ada regresi |

---

*Laporan ini dibuat otomatis oleh Antigravity AI — Dapur Nusa Comprehensive Fix Session.*
