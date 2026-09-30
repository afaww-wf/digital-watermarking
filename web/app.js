const state = {
    imageFile: null,
    watermarkFile: null,
    attackFile: null,
    watermarkSource: "teks",

    lastInsertResult: null,
    lastWatermark: null,

    delta: 25,
    ulang: 3,
};

function $(id) {
    return document.getElementById(id);
}


function showToast(message) {
    const toast = $("toast");
    const text = $("toastMessage");

    if (!toast || !text) return;

    text.textContent = message;

    toast.classList.add("show");

    clearTimeout(window.toastTimer);

    window.toastTimer = setTimeout(() => {
        toast.classList.remove("show");
    }, 2800);
}


async function getErrorMessage(response) {

    try {
        const data = await response.json();

        return data.error || "Terjadi kesalahan pada server.";

    } catch {
        return `Terjadi kesalahan. Status: ${response.status}`;
    }
}


function setButtonLoading(button, loading, text = "Memproses...") {

    if (!button) return;

    if (loading) {

        button.dataset.originalText =
            button.querySelector("span")?.textContent ||
            button.textContent;

        button.classList.add("loading");

        button.disabled = true;

        const span = button.querySelector("span");

        if (span) {
            span.textContent = text;
        } else {
            button.textContent = text;
        }

    } else {

        button.classList.remove("loading");

        button.disabled = false;

        const original =
            button.dataset.originalText;

        if (original) {

            const span = button.querySelector("span");

            if (span) {
                span.textContent = original;
            } else {
                button.textContent = original;
            }
        }
    }
}


function goToPage(pageName) {

    document
        .querySelectorAll(".page")
        .forEach(page => {
            page.classList.remove("active");
        });


    const page = $(`page-${pageName}`);

    if (page) {
        page.classList.add("active");
    }


    document
        .querySelectorAll(".menu-item")
        .forEach(item => {

            item.classList.toggle(
                "active",
                item.dataset.page === pageName
            );

        });


    document
        .querySelectorAll(".process-tab")
        .forEach(tab => {

            tab.classList.toggle(
                "active",
                tab.dataset.page === pageName
            );

        });

    if (pageName === "serangan") {
    perbaruiSebelumSerangan();
     }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function setupNavigation() {

    document
        .querySelectorAll("[data-page]")
        .forEach(element => {

            element.addEventListener("click", () => {

                const page =
                    element.dataset.page;

                if (page) {
                    goToPage(page);
                }

            });

        });
}


/* =========================================================
   MOBILE SIDEBAR
========================================================= */

function setupMobileMenu() {

    const button = $("mobileMenuButton");
    const sidebar = document.querySelector(".sidebar");

    if (!button || !sidebar) return;

    button.addEventListener("click", () => {

        sidebar.classList.toggle("open");

    });


    document
        .querySelectorAll(".menu-item")
        .forEach(item => {

            item.addEventListener("click", () => {

                sidebar.classList.remove("open");

            });

        });
}


function setupImageUpload() {

    const input = $("imageInput");
    const dropzone = $("imageDropzone");

    const wrapper = $("imagePreviewWrapper");
    const preview = $("imagePreview");

    const name = $("imageFileName");
    const dimension = $("imageFileDimension");

    const removeButton =
        $("removeImageButton");


    if (!input || !dropzone) return;


    input.addEventListener("change", () => {

        if (input.files.length > 0) {

            handleImageFile(
                input.files[0]
            );

        }

    });


    dropzone.addEventListener(
        "dragover",
        event => {

            event.preventDefault();

            dropzone.classList.add(
                "dragover"
            );

        }
    );


    dropzone.addEventListener(
        "dragleave",
        () => {

            dropzone.classList.remove(
                "dragover"
            );

        }
    );


    dropzone.addEventListener(
        "drop",
        event => {

            event.preventDefault();

            dropzone.classList.remove(
                "dragover"
            );

            const file =
                event.dataTransfer.files[0];

            if (file) {
                handleImageFile(file);
            }

        }
    );


    removeButton?.addEventListener(
        "click",
        () => {

            state.imageFile = null;

            input.value = "";

            wrapper.classList.add(
                "hidden"
            );

            dropzone.classList.remove(
                "hidden"
            );

        }
    );


    function handleImageFile(file) {

        if (!file.type.startsWith("image/")) {

            showToast(
                "File harus berupa gambar PNG atau JPG."
            );

            return;
        }


        if (file.size > 10 * 1024 * 1024) {

            showToast(
                "Ukuran gambar maksimal 10 MB."
            );

            return;
        }


        state.imageFile = file;


        const objectUrl =
            URL.createObjectURL(file);


        preview.src = objectUrl;

        name.textContent =
            file.name;


        preview.onload = () => {

            dimension.textContent =
                `${preview.naturalWidth} × ${preview.naturalHeight} px`;

            URL.revokeObjectURL(
                objectUrl
            );

        };


        wrapper.classList.remove(
            "hidden"
        );

        dropzone.classList.add(
            "hidden"
        );
    }
}


/* 
   WATERMARK 
 */

function setupWatermarkSource() {

    const textRadio =
        $("textRadio");

    const logoRadio =
        $("logoRadio");

    const textPanel =
        $("textWatermarkPanel");

    const logoPanel =
        $("logoWatermarkPanel");

    const radios =
        document.querySelectorAll(
            'input[name="watermarkSource"]'
        );


    radios.forEach(radio => {

        radio.addEventListener(
            "change",
            () => {

                state.watermarkSource =
                    radio.value;


                document
                    .querySelectorAll(
                        ".radio-option"
                    )
                    .forEach(option => {

                        const input =
                            option.querySelector(
                                "input"
                            );

                        option.classList.toggle(
                            "active",
                            input.checked
                        );

                    });


                if (
                    state.watermarkSource ===
                    "teks"
                ) {

                    textPanel.classList.remove(
                        "hidden"
                    );

                    logoPanel.classList.add(
                        "hidden"
                    );

                } else {

                    textPanel.classList.add(
                        "hidden"
                    );

                    logoPanel.classList.remove(
                        "hidden"
                    );

                }

            }
        );

    });


    const textInput =
        $("watermarkText");


    textInput?.addEventListener(
        "input",
        updateWatermarkText
    );


    updateWatermarkText();


    const logoInput =
        $("watermarkImageInput");


    logoInput?.addEventListener(
        "change",
        () => {

            if (logoInput.files.length) {

                state.watermarkFile =
                    logoInput.files[0];

                showToast(
                    "Logo watermark berhasil dipilih."
                );

                updateLogoPreview(
                    state.watermarkFile
                );

            }

        }
    );


    function updateWatermarkText() {

        const value =
            textInput.value || "";

        $("textCounter").textContent =
            `${value.length}/32`;

        $("watermarkPreviewText")
            .textContent =
            value || "Watermark";
    }


    function updateLogoPreview(file) {

        const url =
            URL.createObjectURL(file);

        const preview =
            $("watermarkPreviewText");

        preview.textContent =
            "LOGO";

        preview.style.fontSize =
            "12px";

        preview.style.letterSpacing =
            "0";

        const image =
            document.createElement("img");

        image.src = url;

        image.style.maxWidth = "80%";
        image.style.maxHeight = "75px";
        image.style.objectFit = "contain";

        preview.replaceWith(image);

        image.id =
            "watermarkPreviewText";

        image.onload = () => {
            URL.revokeObjectURL(url);
        };
    }
}


/* 
   PASSWORD
*/

function setupPassword() {

    const input =
        $("secretKey");

    const button =
        $("togglePassword");


    if (!input || !button) return;


    button.addEventListener(
        "click",
        () => {

            const hidden =
                input.type === "password";


            input.type =
                hidden
                    ? "text"
                    : "password";


            button.textContent =
                hidden
                    ? "🙈"
                    : "👁";

        }
    );
}


/* 
   PARAMETER
*/

function setupParameters() {

    const deltaRange =
        $("deltaRange");

    const deltaValue =
        $("deltaValue");


    deltaRange?.addEventListener(
        "input",
        () => {

            state.delta =
                Number(deltaRange.value);

            deltaValue.textContent =
                state.delta;

        }
    );


    const minus =
        $("repeatMinus");

    const plus =
        $("repeatPlus");

    const display =
        $("repeatDisplay");

    const value =
        $("repeatValue");


    function updateRepeat() {

        display.textContent =
            state.ulang;

        value.textContent =
            `${state.ulang}×`;

    }


    minus?.addEventListener(
        "click",
        () => {

            if (state.ulang > 1) {

                state.ulang -= 2;

                if (state.ulang < 1) {
                    state.ulang = 1;
                }

                updateRepeat();

            }

        }
    );


    plus?.addEventListener(
        "click",
        () => {

            if (state.ulang < 9) {

                state.ulang += 2;

                if (state.ulang > 9) {
                    state.ulang = 9;
                }

                updateRepeat();

            }

        }
    );


    updateRepeat();
}


/* 
   INSERT WATERMARK
*/

function setupInsert() {

    const button =
        $("insertButton");


    if (!button) return;


    button.addEventListener(
        "click",
        async () => {

            if (!state.imageFile) {

                showToast(
                    "Silakan upload citra terlebih dahulu."
                );

                return;
            }


            const key =
                $("secretKey").value.trim();


            if (!key) {

                showToast(
                    "Kunci rahasia tidak boleh kosong."
                );

                return;
            }


            const form =
                new FormData();


            form.append(
                "citra",
                state.imageFile
            );


            form.append(
                "kunci",
                key
            );


            form.append(
                "delta",
                state.delta
            );


            form.append(
                "ulang",
                state.ulang
            );


            form.append(
                "sumber",
                state.watermarkSource
            );


            if (
                state.watermarkSource ===
                "teks"
            ) {

                const text =
                    $("watermarkText")
                        .value
                        .trim();


                if (!text) {

                    showToast(
                        "Teks watermark tidak boleh kosong."
                    );

                    return;
                }


                form.append(
                    "teks",
                    text
                );

            } else {

                if (!state.watermarkFile) {

                    showToast(
                        "Silakan upload logo watermark."
                    );

                    return;
                }


                form.append(
                    "watermark",
                    state.watermarkFile
                );
            }


            setButtonLoading(
                button,
                true,
                "Menyisipkan..."
            );


            try {

                const response =
                    await fetch(
                        "/api/sisip",
                        {
                            method: "POST",
                            body: form
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        await getErrorMessage(
                            response
                        )
                    );

                }


                const data =
                    await response.json();


                state.lastInsertResult =
                    data;


                state.lastWatermark =
                    data.watermark_preview;


                showInsertResult(data);


                showToast(
                    "Watermark berhasil disisipkan."
                );

            } catch (error) {

                showToast(
                    error.message
                );

            } finally {

                setButtonLoading(
                    button,
                    false
                );

            }

        }
    );
}


/* 
   SHOW INSERT RESULT
 */
function showInsertResult(data) {

    $("insertResult").classList.remove("hidden");

    $("resultOriginal").src = data.citra_asli;
    $("resultWatermarked").src = data.citra_watermark;

    $("psnrValue").textContent = `${data.psnr} dB`;

    document
        .querySelector(".result-heading")
        ?.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
}


/* 
   DOWNLOAD RESULT
*/

function setupDownload() {

    const button = $("downloadWatermark");

    if (!button) return;

    button.addEventListener("click", (event) => {

        event.preventDefault();

        const img = $("resultWatermarked");

        if (!img || !img.src || img.naturalWidth === 0) {
            showToast("Belum ada citra hasil untuk diunduh.");
            return;
        }

        const canvas = document.createElement("canvas");
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        canvas.getContext("2d").drawImage(img, 0, 0);

        canvas.toBlob((blob) => {

            const url = URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "citra-watermark.png";

            document.body.appendChild(a);
            a.click();
            a.remove();

            setTimeout(() => URL.revokeObjectURL(url), 1000);

        }, "image/png");
    });
}
/* 
   EXTRAK
*/

function setupExtraction() {

    const input =
        $("extractImageInput");

    const button =
        $("extractButton");

    const useSession =
        $("useSessionButton");

    const useInsertionResult =
    $("useInsertionResult");

    const sessionPreview = $("sessionImagePreview");
    const sessionImage = $("sessionImage");
    const uploadArea = $("extractUploadArea");

    const extractPreview = $("extractPreview");


   input?.addEventListener("change", () => {

    if (!input.files.length) return;

    const file = input.files[0];
    const url = URL.createObjectURL(file);

    $("extractFileName").textContent = file.name;
    extractPreview.src = url;
    extractPreview.onload = () => URL.revokeObjectURL(url);

    $("extractManualPreviewWrapper").classList.remove("hidden");
    $("extractFileInfo").classList.remove("hidden");
    uploadArea.classList.add("hidden");

}); 

    useInsertionResult?.addEventListener("change", () => {

    if (useInsertionResult.checked) {

        if (!state.lastInsertResult) {
            useInsertionResult.checked = false;
            showToast("Belum ada hasil penyisipan. Silakan lakukan penyisipan terlebih dahulu.");
            return;
        }

        sessionImage.src = state.lastInsertResult.citra_watermark;
        sessionPreview.classList.remove("hidden");
        uploadArea.classList.add("hidden");
        $("extractManualPreviewWrapper")?.classList.add("hidden");
        $("extractFileInfo")?.classList.add("hidden");

        showToast("Hasil penyisipan akan digunakan untuk ekstraksi.");

        } else {

        sessionPreview.classList.add("hidden");
        uploadArea.classList.remove("hidden");

        if (input.files.length) {
            $("extractFileInfo")?.classList.remove("hidden");
        }

    }
});


    useSession?.addEventListener(
        "click",
        () => {

            if (
                !state.lastInsertResult
            ) {

                showToast(
                    "Belum ada hasil penyisipan pada halaman ini."
                );

                return;
            }


            showToast(
                "Akan menggunakan hasil penyisipan terakhir."
            );

        }
    );

    


    button?.addEventListener(
        "click",
        async () => {

            const form =
                new FormData();


            const key =
                $("secretKey")
                    .value
                    .trim();


            form.append(
                "kunci",
                key
            );


            form.append(
                "delta",
                state.delta
            );


            form.append(
                "ulang",
                state.ulang
            );


            let pakaiSesi = false;

if (useInsertionResult?.checked) {

    if (!state.lastInsertResult) {

        showToast(
            "Belum ada hasil penyisipan. Silakan lakukan penyisipan terlebih dahulu."
        );

        return;
    }

    pakaiSesi = true;

} else {

    if (!input.files.length) {

        showToast(
            "Silakan unggah citra terlebih dahulu atau gunakan hasil penyisipan."
        );

        return;
    }

    form.append(
        "citra",
        input.files[0]
    );
}


            form.append(
                "pakai_sesi",
                pakaiSesi
                    ? "true"
                    : "false"
            );


            setButtonLoading(
                button,
                true,
                "Mengekstrak..."
            );


            try {

                const response =
                    await fetch(
                        "/api/ekstrak",
                        {
                            method: "POST",
                            body: form
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        await getErrorMessage(
                            response
                        )
                    );

                }


                const data =
                    await response.json();


                showExtractionResult(
                    data
                );


                showToast(
                    "Watermark berhasil diekstrak."
                );

            } catch (error) {

                showToast(
                    error.message
                );

            } finally {

                setButtonLoading(
                    button,
                    false
                );

            }

        }
    );
}


/* 
   HASIL EXTRAK
 */

function showExtractionResult(data) {

    const image =
        $("extractedWatermark");

    const empty =
        $("extractionEmpty");

    $("watermarkResultBox")?.classList.remove("empty"); // ← baris baru    


    image.src =
        data.watermark_hasil;

    image.classList.remove(
        "hidden"
    );

    empty.classList.add(
        "hidden"
    );


    if (data.nc !== undefined) {

        $("extractNC")
            .textContent =
            Number(data.nc)
                .toFixed(4);

    }


    if (data.ber !== undefined) {

        $("extractBER")
            .textContent =
            Number(data.ber)
                .toFixed(4);

    }
}


/*
   LOAD SERANGAN LIST
 */

async function loadAttacks() {

    const select =
        $("attackSelect");


    if (!select) return;


    try {

        const response =
            await fetch(
                "/api/serangan/daftar"
            );


        if (!response.ok) {
            return;
        }


        const attacks =
            await response.json();


        attacks.forEach(
            attack => {

                const option =
                    document.createElement(
                        "option"
                    );

                option.value =
                    attack;

                option.textContent =
                    attack;

                select.appendChild(
                    option
                );

            }
        );

    } catch (error) {

        console.error(
            "Gagal memuat serangan:",
            error
        );

    }
}

function setupAttack() {

    const button = $("runAttackButton");

    button?.addEventListener("click", async () => {

        const attack = $("attackSelect").value;

        if (!attack) {
            showToast("Pilih jenis serangan terlebih dahulu.");
            return;
        }

        setButtonLoading(button, true, "Menguji...");

        try {

            const response = await fetch("/api/serangan", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nama: attack })
            });

            if (!response.ok) {
                throw new Error(await getErrorMessage(response));
            }

            const data = await response.json();

           $("attackBefore").src = data.citra_sebelum;
           $("attackBefore").classList.remove("hidden");
           $("attackBeforeEmpty").classList.add("hidden");

           $("attackAfter").src = data.citra_sesudah;
           $("attackAfter").classList.remove("hidden");
           $("attackAfterEmpty").classList.add("hidden");

           $("attackWatermark").src = data.watermark_hasil;
           $("attackWatermark").classList.remove("hidden");
           $("attackWatermarkBox").classList.remove("empty");

           $("attackNC").textContent = Number(data.nc).toFixed(4);
           $("attackBER").textContent = Number(data.ber).toFixed(4);

            showToast(`Serangan ${attack} selesai.`);

        } catch (error) {
            showToast(error.message);
        } finally {
            setButtonLoading(button, false);
        }
    });

    $("runAllButton")?.addEventListener("click", runAllAttacks);
}

  
/* 
   RUN ALL SERANGAN
 */

async function runAllAttacks() {

    const button =
        $("runAllButton");


    setButtonLoading(
        button,
        true,
        "Menjalankan..."
    );


    try {

        const response =
            await fetch(
                "/api/uji-semua",
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                await getErrorMessage(
                    response
                )
            );

        }


        const results =
            await response.json();


        renderAttackTable(
            results
        );


        showToast(
            "Semua pengujian selesai."
        );

    } catch (error) {

        showToast(
            error.message
        );

    } finally {

        setButtonLoading(
            button,
            false
        );

    }
}


/* 
   EXCEL TABLE
 */

function renderAttackTable(results) {

    const wrapper =
        $("attackTableWrapper");

    const body =
        $("attackTableBody");


    body.innerHTML = "";


    results.forEach(
        item => {

            const row =
                document.createElement(
                    "tr"
                );


            const attackCell =
                document.createElement(
                    "td"
                );

            attackCell.textContent =
                item.serangan;


            const ncCell =
                document.createElement(
                    "td"
                );

            ncCell.textContent =
                Number(item.nc)
                    .toFixed(4);


            const berCell =
                document.createElement(
                    "td"
                );

            berCell.textContent =
                Number(item.ber)
                    .toFixed(4);


            row.appendChild(
                attackCell
            );

            row.appendChild(
                ncCell
            );

            row.appendChild(
                berCell
            );


            body.appendChild(
                row
            );

        }
    );


    wrapper.classList.remove(
        "hidden"
    );

    wrapper.scrollIntoView({
    behavior: "smooth",
    block: "start"
});
}

function perbaruiSebelumSerangan() {

    const beforeImg = $("attackBefore");
    const beforeEmpty = $("attackBeforeEmpty");

    if (state.lastInsertResult) {
        beforeImg.src = state.lastInsertResult.citra_watermark;
        beforeImg.classList.remove("hidden");
        beforeEmpty.classList.add("hidden");
    } else {
        beforeImg.classList.add("hidden");
        beforeEmpty.classList.remove("hidden");
    }

    $("attackAfter").classList.add("hidden");
    $("attackAfterEmpty").classList.remove("hidden");

    $("attackWatermark").classList.add("hidden");
    $("attackWatermarkBox").classList.add("empty");

    $("attackNC").textContent = "--";
    $("attackBER").textContent = "--";
}


/*
   INITIALIZE
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupNavigation();

        setupMobileMenu();

        setupImageUpload();

        setupWatermarkSource();

        setupPassword();

        setupParameters();

        setupInsert();

        setupDownload();

        setupExtraction();

        setupAttack();

        loadAttacks();

        goToPage("beranda");

    }
);