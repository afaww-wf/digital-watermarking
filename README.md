# Digital Watermarking — DCT 8×8 + QIM (Blind Watermarking)

Tugas Proyek Aplikasi Kriptografi — Mata Kuliah Keamanan Informasi
Program Studi Informatika, Fakultas Teknik, Universitas Siliwangi

Aplikasi web untuk menyisipkan (embed) dan mengekstraksi (extract) watermark digital ke dalam citra menggunakan **Discrete Cosine Transform (DCT) blok 8×8** yang dikombinasikan dengan **Quantization Index Modulation (QIM)**. Watermark dapat diekstraksi kembali tanpa memerlukan citra asli (**blind watermarking**), dan diuji ketahanannya terhadap berbagai serangan citra (kompresi JPEG, cropping, resize, noise, perubahan kecerahan dan kontras).

---

## Daftar Isi

- [Fitur](#fitur)
- [Struktur Proyek](#struktur-proyek)
- [Cara Instalasi](#cara-instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Cara Menjalankan Unit Test](#cara-menjalankan-unit-test)
- [Cara Menjalankan Pengujian Otomatis (XLSX)](#cara-menjalankan-pengujian-otomatis-xlsx)
- [Contoh Penggunaan](#contoh-penggunaan)
- [Metrik Pengujian](#metrik-pengujian)
- [Batasan yang Diketahui](#batasan-yang-diketahui)
- [Anggota](#anggota)

---

## Fitur

**Fitur wajib**
- Penyisipan watermark (teks identitas atau gambar logo biner) ke dalam citra grayscale menggunakan DCT blok 8×8 dan QIM
- Ekstraksi watermark bersifat *blind* — tidak memerlukan citra asli
- Kunci rahasia menentukan posisi blok yang dipakai (permutasi acak berbasis kunci)
- Redundansi (pengulangan bit) dengan voting mayoritas untuk meningkatkan ketahanan
- Parameter delta (kekuatan sisip) dan redundansi dapat diatur langsung dari antarmuka
- Pengujian ketahanan terhadap 13 skenario serangan: JPEG (Q90/Q70/Q50), cropping (10%/25%), resize 50%, noise Gaussian (σ=5/10/20), perubahan kecerahan (±20), perubahan kontras (×0.8/×1.2)
- Perhitungan metrik PSNR, Normalized Correlation (NC), dan Bit Error Rate (BER)
- Ekspor hasil pengujian ke berkas XLSX

**Fitur pengayaan**
- Mode blind sepenuhnya (tanpa citra asli sama sekali saat ekstraksi)
- Antarmuka web interaktif dengan tiga alur kerja: Sisipkan → Ekstrak → Serangan & Uji

---

## Struktur Proyek

```
digital-watermarking/
├── core/                   # Modul inti algoritma
│   ├── dct.py              # DCT/IDCT 2D blok 8x8 (ditulis sendiri)
│   ├── common.py           # Parameter bersama & permutasi blok berbasis kunci
│   ├── embed.py            # Penyisipan watermark (QIM)
│   ├── extract.py          # Ekstraksi watermark (voting mayoritas)
│   ├── attacks.py          # Implementasi serangan pengujian
│   └── metrics.py          # PSNR, NC, BER
├── tests/                  # Unit test (15 test)
│   ├── test_dasar.py
│   ├── test_embed_extract.py
│   └── test_attacks.py
├── scripts/
│   └── jalankan_pengujian.py   # Skrip otomatis: uji semua citra & serangan → XLSX
├── data/
│   ├── citra_uji/          # Taruh citra uji (JPG/PNG) di sini
│   ├── hasil_contoh/       # Contoh citra ber-watermark (dibuat otomatis)
│   └── hasil_uji.xlsx      # Hasil pengujian (dibuat otomatis)
├── web/
│   ├── index.html          # Antarmuka aplikasi
│   ├── style.css
│   └── app.js
├── server.py                # Backend Flask (API embed/extract/attack)
├── requirements.txt
└── README.md
```

---

## Cara Instalasi

**1. Clone repositori**
```bash
git clone https://github.com/afaww-wf/digital-watermarking.git
cd digital-watermarking
```

**2. Buat dan aktifkan virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

**3. Install dependensi**
```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan

Jalankan server backend:
```bash
python server.py
```

Buka browser ke:
```
http://localhost:5000
```

Aplikasi akan menampilkan empat halaman: **Beranda**, **Sisipkan**, **Ekstrak**, dan **Serangan & Uji**, yang dapat diakses lewat menu di sidebar kiri.

---

## Cara Menjalankan Unit Test

```bash
python tests/test_dasar.py
python tests/test_embed_extract.py
python tests/test_attacks.py
```

Total terdapat **15 unit test** yang mencakup fungsi DCT/IDCT, pembagian blok, metrik (PSNR/NC/BER), alur sisip-ekstrak, penanganan kunci salah, penolakan watermark yang melebihi kapasitas, dan seluruh fungsi serangan.

---

## Cara Menjalankan Pengujian Otomatis (XLSX)

1. Taruh 5 citra uji (JPG/PNG) di folder `data/citra_uji/`. Jika folder kosong, skrip akan otomatis membuat citra sintetis sebagai contoh.
2. Jalankan:
   ```bash
   python scripts/jalankan_pengujian.py
   ```
3. Hasil pengujian (PSNR, NC, BER untuk setiap kombinasi citra × serangan) tersimpan di `data/hasil_uji.xlsx`, dengan dua sheet: **Hasil Detail** dan **Ringkasan per Serangan**.

---

## Contoh Penggunaan

**Menyisipkan watermark lewat antarmuka web:**
1. Buka halaman **Sisipkan**
2. Unggah citra asli (PNG/JPG)
3. Pilih sumber watermark: ketik teks identitas (misal NPM) atau unggah gambar logo
4. Atur parameter (kunci rahasia, delta, redundansi) di panel kanan bila perlu
5. Klik **Sisipkan Watermark** — hasil PSNR dan citra ber-watermark akan ditampilkan

**Mengekstraksi watermark:**
1. Buka halaman **Ekstrak**
2. Centang "Gunakan hasil penyisipan" untuk memakai citra dari langkah sebelumnya, atau unggah citra lain
3. Masukkan kunci yang sama seperti saat penyisipan
4. Klik **Ekstrak Watermark** — watermark hasil ekstraksi beserta nilai NC dan BER akan ditampilkan

**Menguji ketahanan terhadap serangan:**
1. Buka halaman **Serangan & Uji**
2. Pilih satu jenis serangan dari dropdown untuk demo langsung, atau klik **Uji Semua Serangan** untuk menjalankan seluruh skenario sekaligus
3. Tabel hasil dapat diunduh sebagai berkas XLSX

---

## Metrik Pengujian

| Metrik | Arti | Nilai ideal |
|---|---|---|
| **PSNR** | Kemiripan citra ber-watermark dengan citra asli (dB) | ≥ 30 dB |
| **NC** (Normalized Correlation) | Kemiripan watermark hasil ekstraksi dengan watermark asli | 1.0 |
| **BER** (Bit Error Rate) | Persentase bit watermark yang salah saat diekstraksi | 0.0 |

---

## Batasan yang Diketahui

- **Pemrosesan citra bersifat grayscale.** Watermark disisipkan pada domain frekuensi (DCT) dari kanal kecerahan (luminance) citra, bukan pada kanal warna, mengikuti pendekatan umum pada penelitian watermarking berbasis DCT/QIM. Citra berwarna yang diunggah akan otomatis dikonversi ke grayscale sebelum diproses.
- **Kualitas watermark menurun pada citra dengan area piksel jenuh yang luas** (misalnya area putih atau hitam pekat berukuran besar), karena penyisipan bit memerlukan pergeseran koefisien yang dapat terpotong (clipping) saat nilai piksel hasil melebihi rentang valid [0, 255]. Redundansi bit membantu mengurangi dampak ini pada citra dengan variasi piksel yang wajar.
- Watermark berukuran tetap 32×32 bit.

---

## Anggota

| Nama | NPM |
|---|---|
| Wafa Faujiah | 247006111026 |

