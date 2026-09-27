import numpy as np

from core.embed import sisipkan, _qim_sisip
from core.extract import ekstrak
from core.metrics import ber, nc
from core.dct import bagi_blok, dct2
from core.common import POSISI_KOEF, urutan_blok


def buat_citra_realistis(tinggi=512, lebar=512, seed=0):
    """Citra uji yang TIDAK punya area jenuh besar (beda dari np.zeros()).

    np.zeros() menghasilkan background 100% piksel=0, yaitu kasus paling
    ekstrem untuk clipping (lihat analisis sebelumnya). Fungsi ini memakai
    gradasi + tekstur ringan supaya tiap blok 8x8 punya variasi piksel,
    sehingga QIM selalu punya "ruang gerak" untuk menyisipkan bit.
    """
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:tinggi, 0:lebar]
    # Latar: gradasi halus di sekitar nilai tengah (bukan 0 polos)
    citra = 90 + 40 * np.sin(x / 45.0) + 30 * np.cos(y / 40.0)
    # "Kotak" seperti sebelumnya, tapi sekarang objeknya lebih terang dari
    # latarnya yang sudah tidak sepenuhnya gelap
    citra[100:400, 100:400] += 60
    # Tekstur/derau ringan supaya tidak ada blok yang benar-benar flat
    citra += rng.normal(0, 5, citra.shape)
    return np.clip(citra, 15, 240).astype(np.uint8)  # jaga jarak dari 0 dan 255


def main():
    citra = buat_citra_realistis()

    watermark = np.zeros((32, 32), dtype=np.uint8)
    watermark[8:24, 8:24] = 1

    kunci = "wafa-kunci-123"
    delta = 25.0  # kembali ke nilai wajar (default), bukan 100

    print(f"DELTA YANG DIPAKAI: {delta}")

    citra_watermark = sisipkan(citra, watermark, kunci=kunci, delta=delta, ulang=3)
    print("Watermark berhasil disisipkan.")

    selisih = np.abs(citra_watermark.astype(np.int16) - citra.astype(np.int16))
    print("Perubahan piksel maksimum :", np.max(selisih))
    print("Rata-rata perubahan piksel:", np.mean(selisih))

    print("\nPengujian tanpa serangan.")
    watermark_hasil = ekstrak(citra_watermark, kunci=kunci, delta=delta, ulang=3)

    nilai_ber = ber(watermark, watermark_hasil)
    nilai_nc = nc(watermark, watermark_hasil)

    print("Jumlah bit watermark asli :", np.sum(watermark))
    print("Jumlah bit hasil ekstraksi:", np.sum(watermark_hasil))
    print("Jumlah bit berbeda        :", np.sum(watermark != watermark_hasil))
    print(f"BER : {nilai_ber:.4f}")
    print(f"NC  : {nilai_nc:.4f}")

    # Bandingkan lagi dengan citra LAMA (np.zeros + delta 100) sebagai kontrol,
    # supaya kelihatan jelas bedanya di satu run yang sama.
    print("\n--- Kontrol: citra lama (np.zeros) + delta 100, untuk perbandingan ---")
    citra_lama = np.zeros((512, 512), dtype=np.uint8)
    citra_lama[100:400, 100:400] = 180
    wm_lama = sisipkan(citra_lama, watermark, kunci=kunci, delta=100.0, ulang=3)
    hasil_lama = ekstrak(wm_lama, kunci=kunci, delta=100.0, ulang=3)
    print("BER (citra np.zeros, delta=100):", f"{ber(watermark, hasil_lama):.4f}")


if __name__ == "__main__":
    main()
