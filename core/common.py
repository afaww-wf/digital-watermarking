"""Bagian yang dipakai bersama oleh embed.py dan extract.py.

Penyisipan dan ekstraksi HARUS memakai parameter dan urutan blok yang sama,
maka semuanya dikumpulkan di sini supaya tidak ada perbedaan.
"""
import hashlib

import numpy as np

# Posisi koefisien DCT frekuensi menengah dalam blok 8x8 (baris, kolom).
POSISI_KOEF = (3, 4)

# Langkah kuantisasi QIM. Makin besar = makin tahan serangan, tapi PSNR turun.
DELTA_DEFAULT = 25.0

# Berapa kali tiap bit disisipkan (redundansi). Dipilih ganjil agar voting
# mayoritas tidak pernah seri.
ULANG_DEFAULT = 3


def kunci_ke_seed(kunci: str) -> int:
    """Ubah kunci teks menjadi bilangan seed untuk PRNG.

    Kunci yang sama selalu menghasilkan seed yang sama. SHA-256 dipakai
    hanya sebagai pengubah teks ke angka, bukan sebagai fitur keamanan utama.
    """
    digest = hashlib.sha256(kunci.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def urutan_blok(jumlah_blok: int, kunci: str) -> np.ndarray:
    """Hasilkan urutan acak indeks blok (permutasi) dari kunci.

    Tanpa kunci yang benar, urutan ini tidak bisa ditebak, sehingga orang
    lain tidak tahu blok mana menyimpan bit ke berapa.
    """
    rng = np.random.default_rng(kunci_ke_seed(kunci))
    return rng.permutation(jumlah_blok)


def hitung_kapasitas(tinggi: int, lebar: int, ulang: int = ULANG_DEFAULT) -> int:
    """Jumlah bit watermark maksimum yang muat pada citra ukuran tinggi x lebar."""
    jumlah_blok = (tinggi // 8) * (lebar // 8)
    return jumlah_blok // ulang
