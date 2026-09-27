"""Semua serangan yang dipakai pada tahap pengujian.

Tiap fungsi menerima citra grayscale uint8 dan mengembalikan citra
grayscale uint8 berukuran SAMA (H x W), supaya bisa langsung dipakai
oleh core/extract.py tanpa perlakuan khusus.
"""
import io

import numpy as np
from PIL import Image


def serang_jpeg(citra: np.ndarray, kualitas: int) -> np.ndarray:
    """Simpan sebagai JPEG lalu buka lagi (kompresi lossy).

    kualitas: 90, 70, atau 50 sesuai syarat tugas.
    """
    buf = io.BytesIO()
    Image.fromarray(citra).save(buf, format="JPEG", quality=kualitas)
    buf.seek(0)
    return np.array(Image.open(buf).convert("L"))


def serang_crop(citra: np.ndarray, persen: float) -> np.ndarray:
    """Potong `persen` bagian citra (dari tepi kanan-bawah), lalu isi hitam
    supaya ukuran keluaran tetap sama dengan citra asli.

    persen: 0.10 berarti 10% area terpotong.
    """
    h, w = citra.shape
    potong_h = int(h * np.sqrt(persen))
    potong_w = int(w * np.sqrt(persen))
    hasil = citra.copy()
    hasil[h - potong_h :, :] = 0
    hasil[:, w - potong_w :] = 0
    return hasil


def serang_resize(citra: np.ndarray, skala: float) -> np.ndarray:
    """Perkecil dengan faktor `skala` lalu kembalikan ke ukuran semula.

    skala: 0.5 berarti diperkecil 50% lalu diperbesar lagi.
    """
    h, w = citra.shape
    kecil = Image.fromarray(citra).resize(
        (max(1, int(w * skala)), max(1, int(h * skala))), Image.BILINEAR
    )
    balik = kecil.resize((w, h), Image.BILINEAR)
    return np.array(balik)


def serang_noise_gaussian(citra: np.ndarray, sigma: float, seed: int = 0) -> np.ndarray:
    """Tambahkan derau Gaussian dengan simpangan baku `sigma`."""
    rng = np.random.default_rng(seed)
    derau = rng.normal(0, sigma, citra.shape)
    return np.clip(citra.astype(np.float64) + derau, 0, 255).astype(np.uint8)


def serang_kecerahan(citra: np.ndarray, delta: int) -> np.ndarray:
    """Tambah/kurangi kecerahan sebesar `delta` (boleh negatif)."""
    return np.clip(citra.astype(np.int16) + delta, 0, 255).astype(np.uint8)


def serang_kontras(citra: np.ndarray, faktor: float) -> np.ndarray:
    """Ubah kontras: piksel = (piksel - 128) * faktor + 128."""
    hasil = (citra.astype(np.float64) - 128.0) * faktor + 128.0
    return np.clip(hasil, 0, 255).astype(np.uint8)


# Daftar semua serangan wajib pada tugas, siap dipakai untuk loop pengujian.
# Setiap entri: (nama_tampilan, fungsi_lambda)
DAFTAR_SERANGAN = [
    ("Tanpa serangan", lambda c: c),
    ("JPEG Q90", lambda c: serang_jpeg(c, 90)),
    ("JPEG Q70", lambda c: serang_jpeg(c, 70)),
    ("JPEG Q50", lambda c: serang_jpeg(c, 50)),
    ("Crop 10%", lambda c: serang_crop(c, 0.10)),
    ("Crop 25%", lambda c: serang_crop(c, 0.25)),
    ("Resize 50%", lambda c: serang_resize(c, 0.50)),
    ("Noise sigma=5", lambda c: serang_noise_gaussian(c, 5)),
    ("Noise sigma=10", lambda c: serang_noise_gaussian(c, 10)),
    ("Noise sigma=20", lambda c: serang_noise_gaussian(c, 20)),
    ("Kecerahan +20", lambda c: serang_kecerahan(c, 20)),
    ("Kecerahan -20", lambda c: serang_kecerahan(c, -20)),
    ("Kontras x0.8", lambda c: serang_kontras(c, 0.8)),
    ("Kontras x1.2", lambda c: serang_kontras(c, 1.2)),
]
