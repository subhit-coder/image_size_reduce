from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from PIL import Image
import numpy as np
import io

# ✅ FIX: Import path को सही किया
from backend.compressor import compress_image

# ---------- APP ----------
app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Original-Size", "X-Compressed-Size", "X-Ratio"]
)

# ---------- SMART TARGET COMPRESSION ----------
def compress_to_target(image, format, target_kb):
    buffer = io.BytesIO()
    quality = 90

    while True:
        buffer = io.BytesIO()

        if format == "JPEG":
            image = image.convert("RGB")
            image.save(buffer, format="JPEG", quality=quality, optimize=True)

        elif format == "WEBP":
            image.save(buffer, format="WEBP", quality=quality)

        else:
            image.save(buffer, format="PNG", optimize=True)

        size_kb = len(buffer.getvalue()) / 1024

        if size_kb <= target_kb or quality <= 10:
            break

        quality -= 10

    buffer.seek(0)
    return buffer


# ---------- API ----------
@app.post("/compress")
async def compress_image_api(
    file: UploadFile = File(...),
    k: int = Form(16),
    output_format: str = Form("PNG"),
    target_kb: int = Form(100)
):
    """
    Image compression endpoint using K-means clustering + quality compression
    
    Args:
        file: Image file to compress
        k: Number of color clusters (2-64)
        output_format: Output format (PNG, JPEG, WEBP)
        target_kb: Target file size in KB
    """

    try:
        # ---------- READ IMAGE ----------
        image = Image.open(file.file).convert("RGB")

        # SAFE resize (not too aggressive)
        if image.width > 1200 or image.height > 1200:
            image = image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

        img_array = np.array(image)

        # ---------- ORIGINAL SIZE ----------
        file.file.seek(0, 2)
        original_size = file.file.tell()
        file.file.seek(0)

        # ---------- K-MEANS COMPRESS ----------
        compressed_array = compress_image(img_array, k)
        compressed_image = Image.fromarray(compressed_array)

        # ---------- TARGET KB COMPRESSION ----------
        buffer = compress_to_target(
            compressed_image,
            output_format.upper(),
            target_kb
        )

        # ---------- COMPRESSED SIZE ----------
        compressed_size = len(buffer.getvalue())

        # ---------- RATIO ----------
        ratio = round(original_size / compressed_size, 2) if compressed_size else 0

        # ---------- RESPONSE ----------
        return StreamingResponse(
            buffer,
            media_type=f"image/{output_format.lower()}",
            headers={
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
                "X-Ratio": str(ratio)
            }
        )
    
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}