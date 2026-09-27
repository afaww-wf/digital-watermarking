"""Jalankan seluruh pengujian wajib (PSNR + semua serangan + NC/BER) pada
citra uji di folder data/, lalu simpan hasilnya sebagai data/hasil_uji.xlsx.

Cara pakai:
    1. Taruh 5 citra uji (JPG/PNG) di folder data/citra_uji/
       (boleh foto asli kamu sendiri; kalau kosong, skrip ini otomatis
       membuat citra sintetis sebagai contoh)
    2. Jalankan:  python scripts/jalankan_pengujian.py
    3. Buka data/hasil_uji.xlsx

Skrip ini juga menyimpan contoh citra ber-watermark ke data/hasil_contoh/
supaya bisa dipakai di laporan dan video demo.
"""
import glob
import os
import sys

import numpy as np
import pandas as pd
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.attacks import DAFTAR_SERANGAN  # noqa: E402
from core.dct import potong_kelipatan_8  # noqa: E402
from core.embed import sisipkan  # noqa: E402
from core.extract import ekstrak  # noqa: E402
from core.metrics import ber, nc, psnr  # noqa: E402

FOLDER_CITRA = os.path.join(os.path.dirname(__file__), "..", "data", "citra_uji")
FOLDER_HASIL = os.path.join(os.path.dirname(__file__), "..", "data", "hasil_contoh")
FILE_XLSX = os.path.join(os.path.dirname(__file__), "..", "data", "hasil_uji.xlsx")
KUNCI = "kunci-rahasia-demo"  # ganti sendiri untuk skripsi/demo asli
UKURAN_CITRA = (512, 512)
UKURAN_WM = (32, 32)


def _buat_citra_sintetis(seed: int) -> np.ndarray:
    """Citra contoh dipakai hanya bila data/citra_uji/ kosong."""
    rng = np.random.default_rng(seed)
    h, w = UKURAN_CITRA
    y, x = np.mgrid[0:h, 0:w]
    citra = 90 + 55 * np.sin((x + seed * 30) / 50.0) + 45 * np.cos((y + seed * 20) / 45.0)
    citra[80 + seed * 10 : 260 + seed * 10, 120:340] += 40
    citra += rng.normal(0, 4, citra.shape)
    return np.clip(citra, 0, 255).astype(np.uint8)


def _muat_citra_uji() -> list:
    """Baca semua citra di data/citra_uji/. Bila kosong, buat 5 citra contoh."""
    os.makedirs(FOLDER_CITRA, exist_ok=True)
    berkas = sorted(
        glob.glob(os.path.join(FOLDER_CITRA, "*.png"))
        + glob.glob(os.path.join(FOLDER_CITRA, "*.jpg"))
        + glob.glob(os.path.join(FOLDER_CITRA, "*.jpeg"))
    )
    citra_list = []
    if not berkas:
        print(f"[info] {FOLDER_CITRA} kosong, memakai 5 citra sintetis contoh.")
        print("       Ganti dengan foto asli kamu sendiri sebelum pengumpulan akhir.")
        for i in range(5):
            citra = _buat_citra_sintetis(i)
            nama = f"sintetis_{i+1}.png"
            Image.fromarray(citra).save(os.path.join(FOLDER_CITRA, nama))
            citra_list.append((nama, citra))
    else:
        for path in berkas:
            gambar = Image.open(path).convert("L").resize(UKURAN_CITRA)
            citra_list.append((os.path.basename(path), np.array(gambar)))
    return citra_list


def _watermark_uji() -> np.ndarray:
    rng = np.random.default_rng(42)
    return rng.integers(0, 2, size=UKURAN_WM).astype(np.uint8)


def main():
    os.makedirs(FOLDER_HASIL, exist_ok=True)
    citra_list = _muat_citra_uji()
    wm = _watermark_uji()

    baris = []
    for nama_citra, citra in citra_list:
        citra = potong_kelipatan_8(citra)
        watermarked = sisipkan(citra, wm, KUNCI)
        nilai_psnr = psnr(citra, watermarked)

        Image.fromarray(watermarked).save(
            os.path.join(FOLDER_HASIL, f"watermarked_{nama_citra}")
        )

        for nama_serangan, fungsi_serangan in DAFTAR_SERANGAN:
            diserang = fungsi_serangan(watermarked)
            wm_ekstraksi = ekstrak(diserang, KUNCI, ukuran_wm=UKURAN_WM)
            baris.append(
                {
                    "Citra": nama_citra,
                    "Serangan": nama_serangan,
                    "PSNR (dB)": round(nilai_psnr, 2),
                    "NC": round(nc(wm, wm_ekstraksi), 4),
                    "BER": round(ber(wm, wm_ekstraksi), 4),
                }
            )
        print(f"[selesai] {nama_citra}  PSNR={nilai_psnr:.2f} dB")

    df = pd.DataFrame(baris)

    ringkasan = (
        df.groupby("Serangan")[["NC", "BER"]]
        .mean()
        .round(4)
        .reset_index()
        .rename(columns={"NC": "Rata-rata NC", "BER": "Rata-rata BER"})
    )

    with pd.ExcelWriter(FILE_XLSX, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Hasil Detail", index=False)
        ringkasan.to_excel(writer, sheet_name="Ringkasan per Serangan", index=False)

    print(f"\nSelesai. Hasil tersimpan di: {os.path.abspath(FILE_XLSX)}")
    print(f"Contoh citra ber-watermark di: {os.path.abspath(FOLDER_HASIL)}")


if __name__ == "__main__":
    main()
