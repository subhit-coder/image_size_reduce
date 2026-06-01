// ===============================
// ELEMENTS
// ===============================
const uploadBox = document.getElementById("uploadBox");
const imageInput = document.getElementById("imageInput");

const kSlider = document.getElementById("kSlider");
const kValue = document.getElementById("kValue");

const formatSelect = document.getElementById("format");
const targetKBInput = document.getElementById("targetKB");

const compressBtn = document.getElementById("compressBtn");
const downloadBtn = document.getElementById("downloadBtn");

const originalSizeEl = document.getElementById("originalSize");
const compressedSizeEl = document.getElementById("compressedSize");
const compressionRatioEl = document.getElementById("compressionRatio");

const sizeInfo = document.getElementById("sizeInfo");
const previewComparison = document.getElementById("previewComparison");
const singlePreview = document.getElementById("singlePreview");

// Canvas handling (IMPORTANT: duplicate id="canvas" issue handled)
const canvases = document.querySelectorAll("#canvas");
const originalCanvas = document.getElementById("originalCanvas");
const compressedCanvas = canvases[0];
const singleCanvas = canvases[1];

const oCtx = originalCanvas.getContext("2d");
const cCtx = compressedCanvas.getContext("2d");
const sCtx = singleCanvas.getContext("2d");

// ===============================
// GLOBAL STATE
// ===============================
let img = new Image();
let originalFileSize = 0;
let compressedBlob = null;

// ===============================
// UI EVENTS
// ===============================
kSlider.addEventListener("input", () => {
    kValue.innerText = kSlider.value;
});

uploadBox.addEventListener("click", () => imageInput.click());

uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.style.border = "2px dashed #6366f1";
});

uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFile(file);
});

imageInput.addEventListener("change", (e) => {
    handleFile(e.target.files[0]);
});

// ===============================
// FILE HANDLER
// ===============================
function handleFile(file) {
    if (!file) return;

    originalFileSize = file.size;

    const reader = new FileReader();
    reader.onload = function (e) {
        img = new Image();
        img.onload = function () {
            drawOriginal();
            showUI();
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// ===============================
// DRAW ORIGINAL IMAGE
// ===============================
function drawOriginal() {
    const maxWidth = 500;
    const scale = maxWidth / img.width;
    const w = maxWidth;
    const h = img.height * scale;

    originalCanvas.width = w;
    originalCanvas.height = h;

    oCtx.drawImage(img, 0, 0, w, h);

    // also show single preview initially
    singleCanvas.width = w;
    singleCanvas.height = h;
    sCtx.drawImage(img, 0, 0, w, h);
}

// ===============================
// SHOW UI SECTIONS
// ===============================
function showUI() {
    sizeInfo.style.display = "flex";
    previewComparison.style.display = "flex";
    singlePreview.style.display = "none";

    originalSizeEl.innerText = formatSize(originalFileSize);
}

// ===============================
// COMPRESS BUTTON
// ===============================
compressBtn.addEventListener("click", async () => {
    await compressImage();
});

// ===============================
// MAIN COMPRESSION LOGIC
// ===============================
async function compressImage() {
    const k = parseInt(kSlider.value);
    const format = formatSelect.value;
    const targetKB = parseInt(targetKBInput.value);

    let imageData = oCtx.getImageData(
        0, 0,
        originalCanvas.width,
        originalCanvas.height
    );

    let compressedData = kMeansQuantize(imageData, k);

    cCtx.putImageData(compressedData, 0, 0);

    // convert to blob with quality tuning
    let quality = 0.9;
    let blob = await canvasToBlob(compressedCanvas, format, quality);

    // try to match target size
    while (blob.size / 1024 > targetKB && quality > 0.1) {
        quality -= 0.05;
        blob = await canvasToBlob(compressedCanvas, format, quality);
    }

    compressedBlob = blob;

    updateStats(blob.size);

    downloadBtn.style.display = "block";
}

// ===============================
// K-MEANS COLOR QUANTIZATION
// ===============================
function kMeansQuantize(imageData, k) {
    let data = imageData.data;
    let pixels = [];

    for (let i = 0; i < data.length; i += 4) {
        pixels.push([data[i], data[i + 1], data[i + 2]]);
    }

    let centroids = initCentroids(pixels, k);

    let clusters = new Array(pixels.length);

    for (let iter = 0; iter < 5; iter++) {
        for (let i = 0; i < pixels.length; i++) {
            clusters[i] = closestCentroid(pixels[i], centroids);
        }

        centroids = recomputeCentroids(pixels, clusters, k);
    }

    for (let i = 0; i < pixels.length; i++) {
        let c = centroids[clusters[i]];
        data[i * 4] = c[0];
        data[i * 4 + 1] = c[1];
        data[i * 4 + 2] = c[2];
    }

    return imageData;
}

function initCentroids(pixels, k) {
    let centroids = [];
    for (let i = 0; i < k; i++) {
        centroids.push(pixels[Math.floor(Math.random() * pixels.length)]);
    }
    return centroids;
}

function closestCentroid(pixel, centroids) {
    let minDist = Infinity;
    let index = 0;

    centroids.forEach((c, i) => {
        let dist =
            (pixel[0] - c[0]) ** 2 +
            (pixel[1] - c[1]) ** 2 +
            (pixel[2] - c[2]) ** 2;

        if (dist < minDist) {
            minDist = dist;
            index = i;
        }
    });

    return index;
}

function recomputeCentroids(pixels, clusters, k) {
    let sums = Array(k).fill(0).map(() => [0, 0, 0, 0]);

    for (let i = 0; i < pixels.length; i++) {
        let c = clusters[i];
        sums[c][0] += pixels[i][0];
        sums[c][1] += pixels[i][1];
        sums[c][2] += pixels[i][2];
        sums[c][3] += 1;
    }

    return sums.map(s => [
        s[3] ? s[0] / s[3] : 0,
        s[3] ? s[1] / s[3] : 0,
        s[3] ? s[2] / s[3] : 0
    ]);
}

// ===============================
// CANVAS TO BLOB
// ===============================
function canvasToBlob(canvas, format, quality) {
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob);
        }, format, quality);
    });
}

// ===============================
// STATS UPDATE
// ===============================
function updateStats(compressedSize) {
    compressedSizeEl.innerText = formatSize(compressedSize);

    let saved = 100 - (compressedSize / originalFileSize) * 100;
    compressionRatioEl.innerText = saved.toFixed(2) + "%";
}

// ===============================
// DOWNLOAD
// ===============================
downloadBtn.addEventListener("click", () => {
    if (!compressedBlob) return;

    const url = URL.createObjectURL(compressedBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "compressed-image";
    a.click();
});

// ===============================
// UTIL
// ===============================
function formatSize(bytes) {
    return (bytes / 1024).toFixed(2) + " KB";
}