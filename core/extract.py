"""Ekstraksi watermark (mode blind: tidak butuh citra asli).

Alur:
  citra -> bagi blok -> DCT -> baca paritas koefisien pada blok yang sama
  dengan saat penyisipan -> voting mayoritas dari `ulang` salinan -> watermark
"""
import numpy as np

from core.common import DELTA_DEFAULT, POSISI_KOEF, ULANG_DEFAULT, urutan_blok
from core.dct import bagi_blok, dct2


def ekstrak(
    citra: np.ndarray,
    kunci: str,
    ukuran_wm: tuple = (32, 32),
    delta: float = DELTA_DEFAULT,
    ulang: int = ULANG_DEFAULT,
) -> np.ndarray:
    """Ekstrak watermark biner dari citra.

    ukuran_wm harus sama dengan ukuran watermark saat penyisipan.
    Kunci, delta, dan ulang juga harus sama.
    Keluaran: array uint8 berbentuk ukuran_wm berisi 0/1.
    """
    if citra.ndim != 2:
        raise ValueError("Citra harus grayscale (2D)")
    tinggi, lebar = citra.shape
    if tinggi % 8 or lebar % 8:
        raise ValueError("Tinggi dan lebar citra harus kelipatan 8")

    n = int(ukuran_wm[0] * ukuran_wm[1])

    blok = bagi_blok(citra.astype(np.float64) - 128.0)
    nby, nbx = blok.shape[:2]
    if n * ulang > nby * nbx:
        raise ValueError("Citra terlalu kecil untuk ukuran watermark ini")
    koef = dct2(blok.reshape(-1, 8, 8))

    urutan = urutan_blok(nby * nbx, kunci)
    baris, kolom = POSISI_KOEF

    # Baca satu bit dari tiap salinan: paritas dari round(koefisien / delta).
    salinan = np.zeros((ulang, n), dtype=np.int64)
    for r in range(ulang):
        idx = urutan[r * n : (r + 1) * n]
        q = np.round(koef[idx, baris, kolom] / delta).astype(np.int64)
        salinan[r] = q % 2

    # Voting mayoritas: bit = 1 bila lebih dari separuh salinan bernilai 1.
    bit = (salinan.sum(axis=0) * 2 > ulang).astype(np.uint8)
    return bit.reshape(ukuran_wm)
