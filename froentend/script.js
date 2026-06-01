compressBtn.addEventListener("click", async () => {

    if (!originalFile) {
        alert("Please upload image first");
        return;
    }

    try {

        compressBtn.disabled = true;
        compressBtn.innerText = "Compressing...";

        const formData = new FormData();

        formData.append("file", originalFile);
        formData.append("k", kSlider.value);

        // Output format bhejna
        const selectedFormat =
            format.value.includes("jpeg")
                ? "JPEG"
                : format.value.includes("webp")
                ? "WEBP"
                : "PNG";

        formData.append(
            "output_format",
            selectedFormat
        );

        const response = await fetch(
            "https://image-size-reduce-1.onrender.com/compress",
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error(
                `Compression Failed (${response.status})`
            );
        }

        const blob = await response.blob();

        const imageURL =
            URL.createObjectURL(blob);

        const compressedImg =
            new Image();

        compressedImg.onload = () => {

            canvas.width =
                compressedImg.width;

            canvas.height =
                compressedImg.height;

            ctx.clearRect(
                0,
                0,
                canvas.width,
                canvas.height
            );

            ctx.drawImage(
                compressedImg,
                0,
                0
            );

            previewComparison.style.display =
                "grid";

            sizeInfo.style.display =
                "grid";

            // Headers from FastAPI
            const originalSize =
                Number(
                    response.headers.get(
                        "X-Original-Size"
                    )
                );

            const compressedSize =
                Number(
                    response.headers.get(
                        "X-Compressed-Size"
                    )
                );

            const ratio =
                response.headers.get(
                    "X-Ratio"
                );

            originalSizeDisplay.textContent =
                formatFileSize(
                    originalSize
                );

            compressedSizeDisplay.textContent =
                formatFileSize(
                    compressedSize
                );

            compressionRatioDisplay.textContent =
                ratio + "x";

            // Download button
            downloadBtn.href =
                imageURL;

            downloadBtn.download =
                "compressed." +
                selectedFormat.toLowerCase();

            downloadBtn.style.display =
                "block";

            isCompressed = true;
        };

        compressedImg.src =
            imageURL;

    } catch (error) {

        console.error(error);

        alert(
            "Error: " +
            error.message
        );

    } finally {

        compressBtn.disabled =
            false;

        compressBtn.innerText =
            "🚀 Compress Image";
    }
});