window.addEventListener("DOMContentLoaded", () => {

const imageInput = document.getElementById("imageInput");
const canvas = document.getElementById("canvas");
const originalCanvas = document.getElementById("originalCanvas");
const ctx = canvas.getContext("2d");
const originalCtx = originalCanvas.getContext("2d");

const kSlider = document.getElementById("kSlider");
const kValue = document.getElementById("kValue");

const compressBtn = document.getElementById("compressBtn");
const downloadBtn = document.getElementById("downloadBtn");
const format = document.getElementById("format");

const sizeInfo = document.getElementById("sizeInfo");
const originalSizeDisplay = document.getElementById("originalSize");
const compressedSizeDisplay = document.getElementById("compressedSize");
const compressionRatioDisplay = document.getElementById("compressionRatio");

const uploadBox = document.querySelector(".upload-box");
const previewComparison = document.getElementById("previewComparison");
const singlePreview = document.getElementById("singlePreview");

let originalFile = null;
let originalFileData = null;
let img = null;
let originalImageData = null;
let isCompressed = false;

// ✅ K-slider update
kSlider.addEventListener("input", () => {
    kValue.innerText = kSlider.value;
});

// ✅ Click upload box
uploadBox.addEventListener("click", () => {
    imageInput.click();
});

// ✅ Image upload
imageInput.addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) {
        console.log("No file selected");
        return;
    }

    console.log("📁 File selected:", file.name);

    // Store original file
    originalFile = file;

    // Check file size
    if (file.size > 10 * 1024 * 1024) {
        alert("❌ File बहुत बड़ा है! 10MB से कम upload करो।");
        return;
    }

    // Check file type
    if (!file.type.startsWith("image/")) {
        alert("❌ Valid image file upload करो!");
        return;
    }

    const reader = new FileReader();

    reader.onerror = () => {
        alert("❌ File read करने में error आया!");
        console.error("FileReader error:", reader.error);
    };

    reader.onload = (event) => {
        console.log("📖 FileReader completed");
        img = new Image();

        img.onerror = () => {
            alert("❌ Image corrupt है या invalid format है!");
            console.error("Image load error");
        };

        img.onload = () => {
            console.log("✅ Image loaded! Size:", img.width, "x", img.height);
            
            // Set canvas size to match image aspect ratio
            const maxSize = 500;
            let canvasWidth = img.width;
            let canvasHeight = img.height;

            // Scale down if too large
            if (canvasWidth > maxSize || canvasHeight > maxSize) {
                const ratio = Math.min(maxSize / canvasWidth, maxSize / canvasHeight);
                canvasWidth = canvasWidth * ratio;
                canvasHeight = canvasHeight * ratio;
            }

            canvas.width = canvasWidth;
            canvas.height = canvasHeight;
            originalCanvas.width = canvasWidth;
            originalCanvas.height = canvasHeight;

            // Clear canvas aur draw image
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            originalCtx.fillStyle = "white";
            originalCtx.fillRect(0, 0, originalCanvas.width, originalCanvas.height);
            originalCtx.drawImage(img, 0, 0, originalCanvas.width, originalCanvas.height);

            // Get image data
            try {
                originalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                isCompressed = false;
                downloadBtn.style.display = "none";
                sizeInfo.style.display = "none";
                previewComparison.style.display = "none";
                singlePreview.style.display = "block";
                
                // Show original file size
                showOriginalFileSize(file.size);
                
                console.log("✅ Image ready for compression!");
                uploadBox.style.opacity = "0.5";
            } catch (e) {
                alert("❌ Canvas error: " + e.message);
                console.error("Canvas error:", e);
            }
        };

        // Set image source (from FileReader)
        img.src = event.target.result;
    };

    reader.readAsDataURL(file);
});

// ✅ Show original file size
function showOriginalFileSize(bytes) {
    let sizeText = "";
    if (bytes < 1024) {
        sizeText = bytes + " B";
    } else if (bytes < 1024 * 1024) {
        sizeText = (bytes / 1024).toFixed(2) + " KB";
    } else {
        sizeText = (bytes / 1024 / 1024).toFixed(2) + " MB";
    }
    
    originalSizeDisplay.textContent = sizeText;
    console.log("📊 Original file size:", sizeText);
}

// ✅ Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + " B";
    } else if (bytes < 1024 * 1024) {
        return (bytes / 1024).toFixed(2) + " KB";
    } else {
        return (bytes / 1024 / 1024).toFixed(2) + " MB";
    }
}

// ✅ Drag and drop support
uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = "#a855f7";
    uploadBox.style.background = "#f9f5ff";
});

uploadBox.addEventListener("dragleave", (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = "#6366f1";
    uploadBox.style.background = "white";
});

uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.style.borderColor = "#6366f1";
    uploadBox.style.background = "white";
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        imageInput.files = files;
        const event = new Event("change", { bubbles: true });
        imageInput.dispatchEvent(event);
    }
});

// ✅ Distance function for K-means
function dist(a, b) {
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2;
}

// ✅ Compress image using K-means
function compressImage(k) {
    if (!originalImageData) {
        alert("⚠️ Pehle image upload karo!");
        return;
    }

    console.log("🔄 Compressing with k =", k);
    
    let data = new Uint8ClampedArray(originalImageData.data);

    // Extract RGB pixels
    let pixels = [];
    for (let i = 0; i < data.length; i += 4) {
        pixels.push([data[i], data[i+1], data[i+2]]);
    }

    console.log("📊 Total pixels:", pixels.length);

    // Initialize random centroids
    let centroids = [];
    for (let i = 0; i < k; i++) {
        centroids.push(pixels[Math.floor(Math.random() * pixels.length)]);
    }

    // K-means iterations - बढ़ाया गया iterations के लिए बेहतर quality
    const iterations = k > 32 ? 10 : 8;
    
    for (let iter = 0; iter < iterations; iter++) {
        let clusters = Array.from({length: k}, () => []);

        // Assign pixels to nearest centroid
        for (let p of pixels) {
            let best = 0, min = Infinity;

            for (let i = 0; i < k; i++) {
                let d = dist(p, centroids[i]);
                if (d < min) {
                    min = d;
                    best = i;
                }
            }
            clusters[best].push(p);
        }

        // Update centroids
        for (let i = 0; i < k; i++) {
            if (clusters[i].length === 0) continue;

            let r = 0, g = 0, b = 0;

            for (let p of clusters[i]) {
                r += p[0];
                g += p[1];
                b += p[2];
            }

            centroids[i] = [
                r / clusters[i].length,
                g / clusters[i].length,
                b / clusters[i].length
            ];
        }
    }

    // Create new image with compressed colors
    let newImg = ctx.createImageData(canvas.width, canvas.height);

    for (let i = 0; i < pixels.length; i++) {
        let p = pixels[i];
        let best = 0, min = Infinity;

        // Find nearest centroid
        for (let j = 0; j < k; j++) {
            let d = dist(p, centroids[j]);
            if (d < min) {
                min = d;
                best = j;
            }
        }

        // Set pixel to centroid color
        newImg.data[i*4] = Math.round(centroids[best][0]);
        newImg.data[i*4+1] = Math.round(centroids[best][1]);
        newImg.data[i*4+2] = Math.round(centroids[best][2]);
        newImg.data[i*4+3] = 255;
    }

    // Draw compressed image on canvas
    ctx.putImageData(newImg, 0, 0);
    
    // Calculate compressed file size
    const compressedData = canvas.toDataURL(format.value, 0.95);
    const compressedBytes = Math.round((compressedData.length - 'data:image/png;base64,'.length) * 0.75);
    
    // Display size info
    displaySizeComparison(originalFile.size, compressedBytes);
    
    // Show comparison
    singlePreview.style.display = "none";
    previewComparison.style.display = "grid";
    sizeInfo.style.display = "grid";
    
    // Show download button
    isCompressed = true;
    downloadBtn.style.display = "block";
    console.log("✅ Compression complete!");
}

// ✅ Display size comparison
function displaySizeComparison(originalSize, compressedSize) {
    const saved = originalSize - compressedSize;
    const ratio = (saved / originalSize * 100).toFixed(1);
    
    originalSizeDisplay.textContent = formatFileSize(originalSize);
    compressedSizeDisplay.textContent = formatFileSize(compressedSize);
    compressionRatioDisplay.textContent = ratio + "% 🎉";
    
    console.log("📊 Original:", formatFileSize(originalSize));
    console.log("🗜️  Compressed:", formatFileSize(compressedSize));
    console.log("💾 Saved:", formatFileSize(saved), `(${ratio}%)`);
}

// ✅ Compress button handler
compressBtn.addEventListener("click", () => {
    console.log("🚀 Compress button clicked");
    const kValue = parseInt(kSlider.value);
    compressImage(kValue);
});

// ✅ Download button handler
downloadBtn.addEventListener("click", () => {
    if (!isCompressed) {
        alert("⚠️ Pehle image compress karo!");
        return;
    }

    const ext = format.value.split("/")[1];
    const filename = "compressed." + ext;
    
    const a = document.createElement("a");
    a.download = filename;
    a.href = canvas.toDataURL(format.value, 0.95);
    a.click();
    
    console.log("⬇️ Downloaded:", filename);
});

console.log("✅ Script loaded successfully!");

});