"""Unit test dasar. Jalankan dari folder watermark-app dengan:
    python -m pytest tests/
atau tanpa pytest:
    python tests/test_dasar.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.dct import bagi_blok, dct2, gabung_blok, idct2  # noqa: E402
from core.metrics import ber, nc, psnr  # noqa: E402


def test_dct_idct_bolak_balik():
    rng = np.random.default_rng(0)
    blok = rng.integers(0, 256, size=(8, 8)).astype(np.float64)
    hasil = idct2(dct2(blok))
    assert np.allclose(blok, hasil, atol=1e-9)


def test_bagi_gabung_blok_identik():
    rng = np.random.default_rng(1)
    citra = rng.integers(0, 256, size=(64, 96)).astype(np.float64)
    assert np.array_equal(citra, gabung_blok(bagi_blok(citra)))


def test_psnr_citra_identik_tak_hingga():
    citra = np.full((16, 16), 100, dtype=np.uint8)
    assert psnr(citra, citra) == float("inf")


def test_ber_nol_bila_sama_dan_setengah_bila_terbalik_separuh():
    w = np.array([0, 1, 0, 1])
    assert ber(w, w) == 0.0
    assert ber(w, np.array([0, 1, 1, 0])) == 0.5


def test_nc_satu_bila_sama():
    w = np.array([1, 0, 1, 1, 0, 1], dtype=np.uint8)
    assert abs(nc(w, w) - 1.0) < 1e-12


if __name__ == "__main__":
    tes = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print(f"{len(tes)} tes lulus")
