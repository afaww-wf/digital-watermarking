"""Metrik pengujian watermarking: MSE, PSNR, BER, NC."""
import numpy as np


def mse(a: np.ndarray, b: np.ndarray) -> float:
    """Mean Squared Error antara dua citra berukuran sama."""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    return float(np.mean((a - b) ** 2))


def psnr(asli: np.ndarray, watermarked: np.ndarray) -> float:
    """PSNR dalam dB. Bila kedua citra identik (MSE = 0) hasilnya tak hingga.

    PSNR = 10 * log10(255^2 / MSE)
    """
    m = mse(asli, watermarked)
    if m == 0:
        return float("inf")
    return float(10 * np.log10((255.0 ** 2) / m))


def ber(w_asli: np.ndarray, w_ekstraksi: np.ndarray) -> float:
    """Bit Error Rate = jumlah bit yang salah / total bit (0 sampai 1)."""
    a = np.asarray(w_asli).ravel().astype(int)
    b = np.asarray(w_ekstraksi).ravel().astype(int)
    if a.shape != b.shape:
        raise ValueError("Ukuran watermark asli dan hasil ekstraksi harus sama")
    return float(np.mean(a != b))


def nc(w_asli: np.ndarray, w_ekstraksi: np.ndarray) -> float:
    """Normalized Correlation = sum(w * w') / sqrt(sum(w^2) * sum(w'^2)).

    Bernilai 1 bila kedua watermark sama persis.
    """
    a = np.asarray(w_asli).ravel().astype(np.float64)
    b = np.asarray(w_ekstraksi).ravel().astype(np.float64)
    if a.shape != b.shape:
        raise ValueError("Ukuran watermark asli dan hasil ekstraksi harus sama")
    penyebut = np.sqrt(np.sum(a ** 2) * np.sum(b ** 2))
    if penyebut == 0:
        return 0.0
    return float(np.sum(a * b) / penyebut)
