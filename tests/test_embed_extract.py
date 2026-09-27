"""Unit test penyisipan dan ekstraksi.
Jalankan: python -m pytest tests/   atau   python tests/test_embed_extract.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.embed import sisipkan  # noqa: E402
from core.extract import ekstrak  # noqa: E402
from core.metrics import ber, psnr  # noqa: E402


def _citra_uji(tinggi=512, lebar=512, seed=0):
    """Citra sintetis: gradasi halus + bentuk + sedikit derau (mirip foto)."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:tinggi, 0:lebar]
    citra = 90 + 60 * np.sin(x / 55.0) + 40 * np.cos(y / 40.0)
    citra[100:260, 150:330] += 45
    citra += rng.normal(0, 4, citra.shape)
    return np.clip(citra, 0, 255).astype(np.uint8)


def _watermark(seed=1):
    rng = np.random.default_rng(seed)
    return rng.integers(0, 2, size=(32, 32)).astype(np.uint8)


def test_sisip_ekstrak_tanpa_serangan_ber_nol():
    citra, wm = _citra_uji(), _watermark()
    hasil = sisipkan(citra, wm, "kunci-rahasia")
    diekstrak = ekstrak(hasil, "kunci-rahasia")
    assert ber(wm, diekstrak) == 0.0


def test_psnr_di_atas_30_db():
    citra, wm = _citra_uji(), _watermark()
    hasil = sisipkan(citra, wm, "kunci-rahasia")
    assert psnr(citra, hasil) > 30.0


def test_kunci_salah_gagal_ekstraksi():
    citra, wm = _citra_uji(), _watermark()
    hasil = sisipkan(citra, wm, "kunci-rahasia")
    diekstrak = ekstrak(hasil, "kunci-salah")
    assert ber(wm, diekstrak) > 0.3  # mendekati acak (0,5)


def test_tolak_watermark_melebihi_kapasitas():
    citra = _citra_uji(64, 64)  # hanya 64 blok -> kapasitas 21 bit
    wm = _watermark()  # 1024 bit
    try:
        sisipkan(citra, wm, "kunci")
    except ValueError:
        return
    raise AssertionError("Seharusnya ValueError karena melebihi kapasitas")


def test_ukuran_citra_tidak_berubah():
    citra, wm = _citra_uji(), _watermark()
    hasil = sisipkan(citra, wm, "kunci-rahasia")
    assert hasil.shape == citra.shape and hasil.dtype == np.uint8


if __name__ == "__main__":
    tes = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print(f"{len(tes)} tes lulus")
