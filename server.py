"""Backend Flask
Catatan:
State disimpan di variabel global STATE karena aplikasi ini
untuk demo lokal satu pengguna.
"""

import base64
import io

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_file
from PIL import Image, ImageDraw, ImageFont

from core.attacks import DAFTAR_SERANGAN
from core.common import DELTA_DEFAULT, ULANG_DEFAULT
from core.dct import potong_kelipatan_8
from core.embed import sisipkan
from core.extract import ekstrak
from core.metrics import ber, nc, psnr


app = Flask(__name__, static_folder="web", static_url_path="")

STATE: dict = {}


# FUNGSI BANTU GAMBAR


def img_ke_b64(arr: np.ndarray) -> str:
    """Mengubah array gambar menjadi base64 PNG."""
    buf = io.BytesIO()

    if arr.ndim == 2:
        gambar = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        gambar = Image.fromarray(arr.astype(np.uint8), mode="RGB")

    gambar.save(buf, format="PNG")

    return (
        "data:image/png;base64,"
        + base64.b64encode(buf.getvalue()).decode()
    )


def wm_ke_b64(wm: np.ndarray, skala: int = 6) -> str:
    """Mengubah watermark biner menjadi gambar PNG base64."""
    gambar = Image.fromarray(
        (wm * 255).astype(np.uint8),
        mode="L"
    )

    gambar = gambar.resize(
        (wm.shape[1] * skala, wm.shape[0] * skala),
        Image.NEAREST
    )

    buf = io.BytesIO()
    gambar.save(buf, format="PNG")

    return (
        "data:image/png;base64,"
        + base64.b64encode(buf.getvalue()).decode()
    )


# KONVERSI GAMBAR


def berkas_ke_rgb(berkas) -> np.ndarray:
    """
    Membaca file gambar sebagai RGB.
    Warna asli dipertahankan.
    """
    gambar = Image.open(berkas).convert("RGB")
    return np.array(gambar, dtype=np.uint8)


def rgb_ke_luminance(rgb: np.ndarray) -> np.ndarray:
    """
    Mengambil luminance/grayscale dari gambar RGB.

    Channel luminance inilah yang digunakan untuk proses
    DCT + QIM.
    """
    gambar = Image.fromarray(
        rgb.astype(np.uint8),
        mode="RGB"
    )

    grayscale = gambar.convert("L")

    return np.array(grayscale, dtype=np.uint8)


def gabungkan_luminance(
    rgb_asli: np.ndarray,
    luminance_baru: np.ndarray
) -> np.ndarray:
    """
    Menggabungkan kembali luminance hasil watermark
    dengan informasi warna asli.

    Menggunakan ruang warna YCbCr supaya warna asli
    tetap dipertahankan.
    """

    gambar = Image.fromarray(
        rgb_asli.astype(np.uint8),
        mode="RGB"
    )

    ycbcr = np.array(
        gambar.convert("YCbCr"),
        dtype=np.uint8
    )

    # Ganti channel Y dengan luminance yang sudah
    # diberi watermark.
    ycbcr[:, :, 0] = luminance_baru.astype(np.uint8)

    hasil = Image.fromarray(
        ycbcr,
        mode="YCbCr"
    ).convert("RGB")

    return np.array(hasil, dtype=np.uint8)


def siapkan_citra(berkas):
    """
    Membaca gambar berwarna dan menyiapkan:
    - RGB asli
    - luminance yang sudah dipotong kelipatan 8
    """

    rgb = berkas_ke_rgb(berkas)

    luminance = rgb_ke_luminance(rgb)

    luminance = potong_kelipatan_8(luminance)

    # Ukuran RGB harus mengikuti luminance setelah dipotong.
    tinggi, lebar = luminance.shape

    rgb = rgb[:tinggi, :lebar]

    return rgb, luminance

# WATERMARK TEKS


def teks_ke_watermark(
    teks: str,
    ukuran=(32, 32)
) -> np.ndarray:
    """
    Render teks menjadi watermark biner.
    """

    kandidat_font = [
        "arial.ttf",
        "Arial.ttf",
        "arialbd.ttf",

        "/usr/share/fonts/truetype/liberation/"
        "LiberationSans-Bold.ttf",

        "/usr/share/fonts/truetype/dejavu/"
        "DejaVuSans-Bold.ttf",

        "/System/Library/Fonts/Supplemental/"
        "Arial Bold.ttf",
    ]

    font = None

    for path in kandidat_font:
        try:
            font = ImageFont.truetype(path, 90)
            break
        except OSError:
            continue

    if font is None:
        font = ImageFont.load_default(size=90)

    kanvas = Image.new(
        "L",
        (400, 400),
        color=0
    )

    draw = ImageDraw.Draw(kanvas)

    kotak = draw.textbbox(
        (0, 0),
        teks,
        font=font
    )

    lebar_teks = kotak[2] - kotak[0]
    tinggi_teks = kotak[3] - kotak[1]

    pos = (
        (400 - lebar_teks) // 2 - kotak[0],
        (400 - tinggi_teks) // 2 - kotak[1]
    )

    draw.text(
        pos,
        teks,
        fill=255,
        font=font
    )

    return (
        np.array(
            kanvas.resize(
                ukuran,
                Image.LANCZOS
            )
        ) > 100
    ).astype(np.uint8)



# WATERMARK LOGO


def gambar_ke_watermark(
    berkas,
    ukuran=(32, 32)
) -> np.ndarray:

    gambar = (
        Image.open(berkas)
        .convert("L")
        .resize(ukuran)
    )

    return (
        np.array(gambar) > 127
    ).astype(np.uint8)



# ROUTE HALAMAN


@app.route("/")
def index():
    return app.send_static_file("index.html")



# API DAFTAR SERANGAN


@app.route("/api/serangan/daftar")
def api_daftar_serangan():
    return jsonify(
        [nama for nama, _ in DAFTAR_SERANGAN]
    )



# API SISIPKAN WATERMARK

@app.route("/api/sisip", methods=["POST"])
def api_sisip():

    citra_file = request.files.get("citra")

    if citra_file is None:
        return jsonify(
            error="Citra asli wajib diunggah."
        ), 400

    kunci = request.form.get(
        "kunci",
        "kunci-rahasia-demo"
    )

    delta = float(
        request.form.get(
            "delta",
            DELTA_DEFAULT
        )
    )

    ulang = int(
        request.form.get(
            "ulang",
            ULANG_DEFAULT
        )
    )

    sumber = request.form.get(
        "sumber",
        "teks"
    )

    # --------------------------------------------------------
    # Buat watermark
    # --------------------------------------------------------

    if sumber == "teks":

        teks = request.form.get(
            "teks",
            ""
        )

        if not teks:
            return jsonify(
                error="Teks watermark tidak boleh kosong."
            ), 400

        watermark = teks_ke_watermark(teks)

    else:

        wm_file = request.files.get(
            "watermark"
        )

        if wm_file is None:
            return jsonify(
                error="Gambar logo watermark wajib diunggah."
            ), 400

        watermark = gambar_ke_watermark(
            wm_file
        )

    # --------------------------------------------------------
    # Baca gambar berwarna
    # --------------------------------------------------------

    try:

        rgb_asli, luminance = siapkan_citra(
            citra_file
        )

    except Exception as e:

        return jsonify(
            error=f"Gagal membaca citra: {e}"
        ), 400

    # --------------------------------------------------------
    # Sisipkan watermark pada luminance
    # --------------------------------------------------------

    try:

        luminance_wm = sisipkan(
            luminance,
            watermark,
            kunci,
            delta=delta,
            ulang=ulang
        )

    except ValueError as e:

        return jsonify(
            error=str(e)
        ), 400

    # --------------------------------------------------------
    # Gabungkan kembali dengan warna asli
    # --------------------------------------------------------

    citra_wm_rgb = gabungkan_luminance(
        rgb_asli,
        luminance_wm
    )

    # --------------------------------------------------------
    # PSNR dihitung pada luminance
    # --------------------------------------------------------

    nilai_psnr = psnr(
        luminance,
        luminance_wm
    )

    
    # Simpan state
    

    STATE.update(
        citra_asli_rgb=rgb_asli,
        citra_asli_luminance=luminance,

        citra_watermark=citra_wm_rgb,
        citra_watermark_luminance=luminance_wm,

        watermark_asli=watermark,

        kunci=kunci,
        delta=delta,
        ulang=ulang,
    )

    # Kirim hasil ke frontend
 

    return jsonify(

        citra_asli=img_ke_b64(
            rgb_asli
        ),

        citra_watermark=img_ke_b64(
            citra_wm_rgb
        ),

        watermark_preview=wm_ke_b64(
            watermark
        ),

        psnr=round(
            nilai_psnr,
            2
        ),

        dimensi=(
            f"{luminance.shape[1]}"
            f"×"
            f"{luminance.shape[0]}"
        ),
    )



# API EKSTRAK WATERMARK


@app.route("/api/ekstrak", methods=["POST"])
def api_ekstrak():

    pakai_sesi = (
        request.form.get(
            "pakai_sesi"
        ) == "true"
    )

    kunci = request.form.get(
        "kunci"
    ) or STATE.get(
        "kunci",
        "kunci-rahasia-demo"
    )

    delta = float(
        request.form.get(
            "delta"
        ) or STATE.get(
            "delta",
            DELTA_DEFAULT
        )
    )

    ulang = int(
        request.form.get(
            "ulang"
        ) or STATE.get(
            "ulang",
            ULANG_DEFAULT
        )
    )

    # Gunakan citra dari sesi


    if pakai_sesi:

        if "citra_watermark" not in STATE:

            return jsonify(
                error=(
                    "Belum ada citra "
                    "ber-watermark. "
                    "Sisipkan dulu di halaman Sisipkan."
                )
            ), 400

        citra = STATE[
            "citra_watermark_luminance"
        ]

        ukuran_wm = STATE[
            "watermark_asli"
        ].shape

    # Upload citra lain
  

    else:

        citra_file = request.files.get(
            "citra"
        )

        if citra_file is None:

            return jsonify(
                error="Citra wajib diunggah."
            ), 400

        try:

            _, citra = siapkan_citra(
                citra_file
            )

        except Exception as e:

            return jsonify(
                error=f"Gagal membaca citra: {e}"
            ), 400

        ukuran_wm = (32, 32)

    # Ekstraksi
   

    try:

        hasil = ekstrak(
            citra,
            kunci,
            ukuran_wm=ukuran_wm,
            delta=delta,
            ulang=ulang
        )

    except ValueError as e:

        return jsonify(
            error=str(e)
        ), 400

    resp = {
        "watermark_hasil": wm_ke_b64(
            hasil
        )
    }

    
    # Metrik
   

    if pakai_sesi:

        wm_asli = STATE[
            "watermark_asli"
        ]

        resp["nc"] = round(
            float(
                nc(
                    wm_asli,
                    hasil
                )
            ),
            4
        )

        resp["ber"] = round(
            float(
                ber(
                    wm_asli,
                    hasil
                )
            ),
            4
        )

        resp["kunci_cocok"] = (
            kunci == STATE["kunci"]
        )

    return jsonify(resp)



# API SATU SERANGAN


@app.route("/api/serangan", methods=["POST"])
def api_serangan():

    if "citra_watermark" not in STATE:

        return jsonify(
            error=(
                "Sisipkan watermark "
                "dulu di halaman Sisipkan."
            )
        ), 400

    data = (
        request.get_json(
            silent=True
        )
        or request.form
    )

    nama = data.get("nama")

    fn = dict(
        DAFTAR_SERANGAN
    ).get(nama)

    if fn is None:

        return jsonify(
            error="Nama serangan tidak dikenal."
        ), 400

    citra_wm = STATE[
        "citra_watermark"
    ]

    wm_asli = STATE[
        "watermark_asli"
    ]

    # Serangan bekerja pada citra RGB
    

    citra_serangan_rgb = fn(
        rgb_ke_luminance(citra_wm)
    )

    hasil = ekstrak(
        citra_serangan_rgb,
        STATE["kunci"],
        ukuran_wm=wm_asli.shape,
        delta=STATE["delta"],
        ulang=STATE["ulang"],
    )

    # Buat preview hasil serangan grayscale.
    citra_serangan_preview = citra_serangan_rgb

    return jsonify(

        citra_sebelum=img_ke_b64(
            citra_wm
        ),

        citra_sesudah=img_ke_b64(
            citra_serangan_preview
        ),

        watermark_hasil=wm_ke_b64(
            hasil
        ),

        nc=round(
            float(
                nc(
                    wm_asli,
                    hasil
                )
            ),
            4
        ),

        ber=round(
            float(
                ber(
                    wm_asli,
                    hasil
                )
            ),
            4
        ),
    )

# API SEMUA SERANGAN


@app.route("/api/uji-semua", methods=["POST"])
def api_uji_semua():

    if "citra_watermark" not in STATE:

        return jsonify(
            error=(
                "Sisipkan watermark "
                "dulu di halaman Sisipkan."
            )
        ), 400

    citra_wm = STATE[
        "citra_watermark"
    ]

    wm_asli = STATE[
        "watermark_asli"
    ]

    # Gunakan luminance untuk pengujian
    citra_wm_luminance = rgb_ke_luminance(
        citra_wm
    )

    hasil = []

    for nama, fn in DAFTAR_SERANGAN:

        citra_serangan = fn(
            citra_wm_luminance
        )

        wm_hasil = ekstrak(
            citra_serangan,
            STATE["kunci"],
            ukuran_wm=wm_asli.shape,
            delta=STATE["delta"],
            ulang=STATE["ulang"],
        )

        hasil.append(
            {
                "serangan": nama,

                "nc": round(
                    float(
                        nc(
                            wm_asli,
                            wm_hasil
                        )
                    ),
                    4
                ),

                "ber": round(
                    float(
                        ber(
                            wm_asli,
                            wm_hasil
                        )
                    ),
                    4
                ),
            }
        )

    STATE[
        "hasil_uji_terakhir"
    ] = hasil

    return jsonify(hasil)


# API DOWNLOAD XLSX


@app.route("/api/uji-semua/xlsx")
def api_uji_semua_xlsx():

    hasil = STATE.get(
        "hasil_uji_terakhir"
    )

    if not hasil:

        return jsonify(
            error=(
                "Jalankan "
                "'Uji Semua Serangan' "
                "dulu."
            )
        ), 400

    df = pd.DataFrame(
        hasil
    )

    buf = io.BytesIO()

    with pd.ExcelWriter(
        buf,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Hasil Uji",
            index=False
        )

    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name=(
            "hasil_uji_interaktif.xlsx"
        ),
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )

# JALANKAN SERVER


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )