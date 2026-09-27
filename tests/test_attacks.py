"""Unit test modul serangan.
Jalankan: python -m pytest tests/   atau   python tests/test_attacks.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.attacks import (  # noqa: E402
    DAFTAR_SERANGAN,
    serang_crop,
    serang_jpeg,
    serang_kecerahan,
    serang_kontras,
    serang_noise_gaussian,
    serang_resize,
)


def _citra_uji():
    rng = np.random.default_rng(0)
    return rng.integers(0, 256, size=(256, 256), dtype=np.uint8)


def test_semua_serangan_menjaga_ukuran():
    citra = _citra_uji()
    for nama, fn in DAFTAR_SERANGAN:
        hasil = fn(citra)
        assert hasil.shape == citra.shape, f"{nama} mengubah ukuran citra"
        assert hasil.dtype == np.uint8, f"{nama} mengubah tipe data"


def test_jpeg_mengubah_nilai_piksel():
    citra = _citra_uji()
    hasil = serang_jpeg(citra, 50)
    assert not np.array_equal(citra, hasil)


def test_crop_membuat_area_hitam():
    citra = np.full((256, 256), 200, dtype=np.uint8)
    hasil = serang_crop(citra, 0.25)
    assert (hasil == 0).sum() > 0


def test_kecerahan_menaikkan_rata_rata():
    citra = _citra_uji()
    hasil = serang_kecerahan(citra, 20)
    assert hasil.astype(np.int32).mean() > citra.astype(np.int32).mean()


def test_resize_bolak_balik_ukuran_tetap():
    citra = _citra_uji()
    hasil = serang_resize(citra, 0.5)
    assert hasil.shape == citra.shape


if __name__ == "__main__":
    tes = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for t in tes:
        t()
        print("OK  ", t.__name__)
    print(f"{len(tes)} tes lulus")
