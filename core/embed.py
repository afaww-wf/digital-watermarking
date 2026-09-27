"""Penyisipan watermark dengan DCT blok 8x8 + QIM.

Alur:
  citra -> bagi blok 8x8 -> DCT -> ubah 1 koefisien menengah per blok
  sesuai bit watermark (QIM) -> IDCT -> gabung blok -> citra ber-watermark
"""
import numpy as np

from core.common import (
    DELTA_DEFAULT,
    POSISI_KOEF,
    ULANG_DEFAULT,
    hitung_kapasitas,
    urutan_blok,
)
from core.dct import bagi_blok, dct2, gabung_blok, idct2


def _qim_sisip(koef: np.ndarray, bit: np.ndarray, delta: float) -> np.ndarray:
    """Sisipkan bit ke dalam nilai koefisien dengan QIM (vektor).

    Aturan:
      bit 0 -> koefisien menjadi kelipatan delta GENAP (0, 2d, 4d, ...)
      bit 1 -> koefisien menjadi kelipatan delta GANJIL (d, 3d, 5d, ...)
    """
    posisi = koef / delta
    q = np.round(posisi)
    # Paritas q sekarang tidak cocok dengan bit -> geser ke tetangga terdekat.
    salah = (q.astype(np.int64) % 2) != bit
    arah = np.where(posisi >= q, 1.0, -1.0)  # geser ke sisi tempat koef berada
    q = np.where(salah, q + arah, q)
    return q * delta


def sisipkan(
    citra: np.ndarray,
    watermark: np.ndarray,
    kunci: str,
    delta: float = DELTA_DEFAULT,
    ulang: int = ULANG_DEFAULT,
) -> np.ndarray:
    """Sisipkan watermark biner ke citra grayscale.

    citra     : array 2D uint8, tinggi dan lebar kelipatan 8
    watermark : array biner (0/1), bentuk bebas (misal 32x32)
    kunci     : teks rahasia (menentukan blok mana yang dipakai)
    Keluaran  : citra ber-watermark, array 2D uint8
    """
    if citra.ndim != 2:
        raise ValueError("Citra harus grayscale (2D)")
    tinggi, lebar = citra.shape
    if tinggi % 8 or lebar % 8:
        raise ValueError("Tinggi dan lebar citra harus kelipatan 8")

    bit = np.asarray(watermark).ravel().astype(np.int64)
    if not np.isin(bit, (0, 1)).all():
        raise ValueError("Watermark harus biner (hanya 0 dan 1)")

    # Langkah 1: cek kapasitas, tolak bila watermark terlalu besar.
    kapasitas = hitung_kapasitas(tinggi, lebar, ulang)
    if bit.size > kapasitas:
        raise ValueError(
            f"Watermark {bit.size} bit melebihi kapasitas {kapasitas} bit"
        )

    # Langkah 2: bagi blok dan DCT semua blok sekaligus.
    blok = bagi_blok(citra.astype(np.float64) - 128.0)
    nby, nbx = blok.shape[:2]
    koef = dct2(blok.reshape(-1, 8, 8))  # (jumlah_blok, 8, 8)

    # Langkah 3: urutan blok acak dari kunci, lalu petakan bit ke blok.
    # Bit ke-i disimpan di `ulang` blok berbeda: r*n + i untuk r = 0..ulang-1.
    urutan = urutan_blok(nby * nbx, kunci)
    n = bit.size
    baris, kolom = POSISI_KOEF
    for r in range(ulang):
        idx = urutan[r * n : (r + 1) * n]
        koef[idx, baris, kolom] = _qim_sisip(koef[idx, baris, kolom], bit, delta)

    # Langkah 4: IDCT, gabung blok, kembalikan ke rentang piksel 0..255.
    hasil = idct2(koef).reshape(nby, nbx, 8, 8)
    hasil = gabung_blok(hasil) + 128.0
    return np.clip(np.round(hasil), 0, 255).astype(np.uint8)
