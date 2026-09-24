"""DCT 2D blok 8x8 yang ditulis sendiri (tanpa scipy.fft.dctn / cv2.dct).

Ide dasarnya: DCT 2D bisa dihitung dengan perkalian matriks.
    koefisien = C @ blok @ C.T
    blok      = C.T @ koefisien @ C
dengan C adalah matriks basis DCT ukuran 8x8.
"""
import numpy as np

N = 8  # ukuran blok


def _buat_matriks_dct(n: int = N) -> np.ndarray:
    """Bangun matriks basis DCT-II ortonormal ukuran n x n.

    C[k, i] = alpha(k) * cos((2i + 1) * k * pi / (2n))
    alpha(0) = sqrt(1/n), alpha(k>0) = sqrt(2/n)
    """
    c = np.zeros((n, n), dtype=np.float64)
    for k in range(n):
        alpha = np.sqrt(1.0 / n) if k == 0 else np.sqrt(2.0 / n)
        for i in range(n):
            c[k, i] = alpha * np.cos((2 * i + 1) * k * np.pi / (2 * n))
    return c


C = _buat_matriks_dct()


def dct2(blok: np.ndarray) -> np.ndarray:
    """DCT 2D satu blok 8x8. Masukan: nilai piksel (float)."""
    return C @ blok @ C.T


def idct2(koef: np.ndarray) -> np.ndarray:
    """Kebalikan dct2: dari koefisien kembali ke nilai piksel."""
    return C.T @ koef @ C


def bagi_blok(citra: np.ndarray) -> np.ndarray:
    """Bagi citra grayscale (H x W) menjadi blok 8x8.

    Keluaran berbentuk (H/8, W/8, 8, 8).
    Tinggi dan lebar harus kelipatan 8 (potong dulu bila belum).
    """
    h, w = citra.shape
    if h % N != 0 or w % N != 0:
        raise ValueError("Tinggi dan lebar citra harus kelipatan 8")
    return (
        citra.reshape(h // N, N, w // N, N)
        .swapaxes(1, 2)
        .copy()
    )


def gabung_blok(blok: np.ndarray) -> np.ndarray:
    """Kebalikan bagi_blok: (H/8, W/8, 8, 8) menjadi citra (H x W)."""
    nby, nbx, _, _ = blok.shape
    return blok.swapaxes(1, 2).reshape(nby * N, nbx * N)


def potong_kelipatan_8(citra: np.ndarray) -> np.ndarray:
    """Potong sisi kanan/bawah agar ukuran citra kelipatan 8."""
    h, w = citra.shape[:2]
    return citra[: h - h % N, : w - w % N]
