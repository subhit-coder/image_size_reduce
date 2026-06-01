import streamlit as st
from PIL import Image
import numpy as np
import io
import os

from backend.compressor import compress_image

st.set_page_config(
    page_title="Subh Image Compressor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
section.main,
.main .block-container {
    background: #eef2ff !important;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 50% -5%, rgba(99,102,241,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 95% 100%, rgba(16,185,129,0.12) 0%, transparent 55%),
        radial-gradient(ellipse 40% 30% at 0% 80%,  rgba(168,85,247,0.08) 0%, transparent 50%),
        #eef2ff !important;
    min-height: 100vh;
}

[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }

.block-container {
    padding: 2rem 3rem 5rem !important;
    max-width: 1280px !important;
}

h1,h2,h3,h4      { font-family: 'Syne', sans-serif !important; }
p,label,span,div { font-family: 'DM Sans', sans-serif !important; }

/* ── HERO ── */
.hero-wrapper {
    text-align: center;
    padding: 3.5rem 0 3rem;
    margin-bottom: 2rem;
    animation: fadeDown 0.7s cubic-bezier(.22,1,.36,1) both;
}
@keyframes fadeDown {
    from { opacity:0; transform:translateY(-24px); }
    to   { opacity:1; transform:translateY(0); }
}

.hero-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.10));
    border: 1px solid rgba(99,102,241,0.28);
    border-radius: 100px;
    padding: 6px 20px;
    font-size: 11.5px;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #4338ca;
    margin-bottom: 1.4rem;
    font-family: 'DM Sans', sans-serif !important;
}
.chip-dot {
    width: 7px; height: 7px;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    border-radius: 50%;
    animation: blink 2s ease-in-out infinite;
}
@keyframes blink {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.3; transform:scale(0.6); }
}

.hero-title {
    font-size: clamp(2.8rem, 6vw, 4.8rem) !important;
    font-weight: 800 !important;
    line-height: 1.05 !important;
    letter-spacing: -0.03em !important;
    color: #1e1b4b !important;
    margin: 0 0 0.6rem !important;
    font-family: 'Syne', sans-serif !important;
}
.hero-title span {
    color: #6366f1 !important;
}

.hero-sub {
    font-size: 1.1rem;
    color: #64748b;
    font-weight: 400;
    max-width: 500px;
    margin: 0 auto 2rem;
    line-height: 1.7;
}

.hero-stats {
    display: inline-flex;
    gap: 2rem;
    background: #ffffff;
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 100px;
    padding: 0.7rem 2rem;
    box-shadow: 0 4px 20px rgba(99,102,241,0.08);
    margin-bottom: 2.5rem;
    animation: fadeUp 0.8s 0.2s cubic-bezier(.22,1,.36,1) both;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(16px); }
    to   { opacity:1; transform:translateY(0); }
}
.hero-stat {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 13px;
    font-weight: 500;
    color: #475569;
    font-family: 'DM Sans', sans-serif !important;
}
.hero-stat-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
}

.hero-line {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent,
        rgba(99,102,241,0.30) 25%, rgba(168,85,247,0.30) 50%,
        rgba(52,211,153,0.30) 75%, transparent);
}

/* ── UPLOAD ZONE ── */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed rgba(99,102,241,0.35) !important;
    border-radius: 24px !important;
    padding: 2.5rem !important;
    transition: all .3s ease !important;
    box-shadow: 0 4px 24px rgba(99,102,241,0.07),
                inset 0 0 0 0 rgba(99,102,241,0) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,102,241,0.65) !important;
    background: rgba(99,102,241,0.02) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,0.13) !important;
    transform: translateY(-2px);
}
[data-testid="stFileUploaderDropzone"] { background: transparent !important; }
[data-testid="stFileUploadDropzone"] button {
    background: linear-gradient(135deg,rgba(99,102,241,0.12),rgba(168,85,247,0.08)) !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    color: #4338ca !important;
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: all .2s !important;
    padding: .55rem 1.5rem !important;
}
[data-testid="stFileUploadDropzone"] button:hover {
    background: rgba(99,102,241,0.22) !important;
    transform: translateY(-1px) !important;
}

/* ── SECTION HEADING ── */
.section-heading {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 2.2rem 0 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'DM Sans', sans-serif !important;
}
.section-heading::before {
    content: '';
    width: 18px; height: 2px;
    background: linear-gradient(90deg,#6366f1,#a855f7);
    border-radius: 2px;
    flex-shrink: 0;
}
.section-heading::after {
    content: '';
    flex: 1; height: 1px;
    background: rgba(99,102,241,0.12);
}

/* ── SLIDER ── */
[data-testid="stSlider"] {
    background: #ffffff !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 20px !important;
    padding: 1.4rem 1.6rem 1rem !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.07) !important;
}
[data-testid="stSlider"] label p {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #1e293b !important;
    font-family: 'DM Sans', sans-serif !important;
    margin-bottom: 0.8rem !important;
}
div[data-baseweb="slider"] div[data-testid="stTickBar"] {
    display: none !important;
}
div[data-baseweb="slider"] > div {
    background: #ede9fe !important;
    height: 8px !important;
    border-radius: 8px !important;
}
div[data-baseweb="slider"] > div > div:first-child {
    background: linear-gradient(90deg, #6366f1, #a855f7) !important;
    height: 8px !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.35) !important;
}
div[data-baseweb="slider"] div[role="slider"] {
    background: #ffffff !important;
    border: 3px solid #6366f1 !important;
    width: 22px !important;
    height: 22px !important;
    box-shadow: 0 0 0 5px rgba(99,102,241,0.15), 0 2px 8px rgba(99,102,241,0.30) !important;
    top: -7px !important;
}
div[data-baseweb="slider"] div[role="slider"]:hover {
    box-shadow: 0 0 0 8px rgba(99,102,241,0.20), 0 2px 12px rgba(99,102,241,0.40) !important;
    border-color: #a855f7 !important;
}
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    color: #6366f1 !important;
    background: linear-gradient(135deg,#6366f1,#a855f7) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: #ffffff !important;
    border: 1.5px solid rgba(99,102,241,0.22) !important;
    border-radius: 14px !important;
    color: #1e293b !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color .2s, box-shadow .2s !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.05) !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: rgba(99,102,241,0.55) !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.10) !important;
}
[data-testid="stSelectbox"] label {
    font-size: 13px !important;
    color: #64748b !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── COMPRESS BUTTON ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg,#6366f1 0%,#a855f7 100%) !important;
    border: none !important;
    border-radius: 16px !important;
    color: #ffffff !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    letter-spacing: .04em !important;
    padding: .85rem 2.5rem !important;
    width: 100% !important;
    height: auto !important;
    transition: all .3s cubic-bezier(.34,1.56,.64,1) !important;
    box-shadow: 0 6px 28px rgba(99,102,241,0.35) !important;
    margin-top: 1.2rem !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-4px) scale(1.015) !important;
    box-shadow: 0 12px 36px rgba(99,102,241,0.50) !important;
    background: linear-gradient(135deg,#818cf8 0%,#c084fc 100%) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(-1px) scale(.98) !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg,rgba(16,185,129,0.10),rgba(5,150,105,0.08)) !important;
    border: 1.5px solid rgba(16,185,129,0.40) !important;
    border-radius: 16px !important;
    color: #065f46 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: .8rem 2rem !important;
    width: 100% !important;
    height: auto !important;
    transition: all .25s ease !important;
    box-shadow: 0 4px 18px rgba(16,185,129,0.14) !important;
    margin-top: 1rem !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: linear-gradient(135deg,rgba(16,185,129,0.22),rgba(5,150,105,0.16)) !important;
    border-color: rgba(16,185,129,0.65) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 28px rgba(16,185,129,0.22) !important;
}

/* ── STAT CARDS ── */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 16px;
    margin: 1.8rem 0;
}
.stat-card {
    background: #ffffff;
    border: 1px solid rgba(99,102,241,0.12);
    border-radius: 20px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(99,102,241,0.07);
    transition: all .25s ease;
    animation: popUp .5s cubic-bezier(.34,1.4,.64,1) both;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content:'';
    position:absolute;
    top:0;left:0;right:0;
    height:3px;
    border-radius:20px 20px 0 0;
}
.stat-original::before  { background: linear-gradient(90deg,#f97316,#fb923c); }
.stat-compressed::before { background: linear-gradient(90deg,#10b981,#34d399); }
.stat-ratio::before      { background: linear-gradient(90deg,#6366f1,#a855f7); }

.stat-card:hover {
    border-color: rgba(99,102,241,0.25);
    transform: translateY(-5px);
    box-shadow: 0 10px 32px rgba(99,102,241,0.13);
}
.stat-card:nth-child(1) { animation-delay:.06s; }
.stat-card:nth-child(2) { animation-delay:.14s; }
.stat-card:nth-child(3) { animation-delay:.22s; }
@keyframes popUp {
    from { opacity:0; transform:translateY(22px) scale(.93); }
    to   { opacity:1; transform:translateY(0) scale(1); }
}
.stat-icon   { font-size:1.6rem; margin-bottom:.5rem; }
.stat-value  {
    font-family:'Syne',sans-serif;
    font-size:1.65rem;
    font-weight:800;
    letter-spacing:-.025em;
    margin:0;
    color:#1e293b;
}
.stat-label  {
    font-size:11px;
    color:#94a3b8;
    font-weight:600;
    letter-spacing:.06em;
    text-transform:uppercase;
    margin-top:5px;
    font-family:'DM Sans',sans-serif;
}
.stat-original  .stat-value { color:#ea580c; }
.stat-compressed .stat-value { color:#059669; }
.stat-ratio     .stat-value { color:#6366f1; }

/* ── IMAGE ── */
[data-testid="stImage"] img {
    border-radius: 18px !important;
    display: block !important;
    box-shadow: 0 6px 30px rgba(99,102,241,0.12) !important;
    transition: transform .3s ease, box-shadow .3s ease !important;
}
[data-testid="stImage"] img:hover {
    transform: scale(1.01) !important;
    box-shadow: 0 12px 40px rgba(99,102,241,0.18) !important;
}

/* ── SUCCESS ALERT ── */
[data-testid="stAlert"] {
    background: linear-gradient(135deg,rgba(16,185,129,0.08),rgba(5,150,105,0.05)) !important;
    border: 1px solid rgba(16,185,129,0.28) !important;
    border-radius: 16px !important;
    color: #065f46 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
}

/* ── INFO BADGE ── */
.info-pill {
    display:inline-flex; align-items:center;
    border-radius:100px; padding:5px 16px;
    font-size:12.5px; font-weight:500;
    font-family:'DM Sans',sans-serif;
    transition: transform .2s, box-shadow .2s;
}
.info-pill:hover {
    transform:translateY(-2px);
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

hr {
    border:none !important;
    border-top:1px solid rgba(99,102,241,0.10) !important;
    margin:2rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
  <h1 class="hero-title">Subh <span>Image</span> Compressor</h1>
  <div style="display:flex;justify-content:center;">
    <div class="hero-stats">
      <div class="hero-stat">
        <span class="hero-stat-dot" style="background:#6366f1;"></span>
        K-Means Powered
      </div>
      <div class="hero-stat">
        <span class="hero-stat-dot" style="background:#10b981;"></span>
        JPEG · PNG · WEBP
      </div>
      <div class="hero-stat">
        <span class="hero-stat-dot" style="background:#f97316;"></span>
        Up to 90% Smaller
      </div>
    </div>
  </div>
  <div class="hero-line"></div>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD ──────────────────────────────────────────────────────
st.markdown('<p class="section-heading">01 — Upload your image</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Drop your image here, or click to browse",
    type=["jpg","jpeg","png"],
    label_visibility="collapsed"
)

if uploaded_file is not None:

    image     = Image.open(uploaded_file)
    image.thumbnail((800, 800))
    img_array = np.array(image)

    h, w      = img_array.shape[:2]
    channels  = img_array.shape[2] if img_array.ndim == 3 else 1

    st.markdown(f"""
    <div style="display:flex;gap:10px;margin:1rem 0 2rem;flex-wrap:wrap;">
      <span class="info-pill" style="background:rgba(99,102,241,0.09);border:1px solid rgba(99,102,241,0.22);color:#4338ca;">
        📐 {w} × {h} px
      </span>
      <span class="info-pill" style="background:rgba(16,185,129,0.09);border:1px solid rgba(16,185,129,0.22);color:#065f46;">
        🎨 {channels} channel{"s" if channels>1 else ""}
      </span>
      <span class="info-pill" style="background:rgba(249,115,22,0.09);border:1px solid rgba(249,115,22,0.22);color:#9a3412;">
        📄 {uploaded_file.name}
      </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<p class="section-heading">02 — Original image</p>', unsafe_allow_html=True)
        st.image(image, use_container_width=True)

    st.markdown('<p class="section-heading">03 — Compression settings</p>', unsafe_allow_html=True)

    col_settings, col_fmt = st.columns([3, 1])

    with col_settings:
        k = st.slider(
            "🎨 Color Palette Size (K)  —  8 = Smallest file   |   64 = Best quality",
            min_value=8, max_value=64, value=16
        )

    with col_fmt:
        output_format = st.selectbox("📁 Output Format", ["JPEG", "PNG", "WEBP"])

    compress_btn = st.button("⚡  Compress Now", use_container_width=True)

    if compress_btn:

        with st.spinner("Applying K-Means clustering…"):
            compressed_img = compress_image(img_array, k)

        with col2:
            st.markdown('<p class="section-heading">04 — Compressed result</p>', unsafe_allow_html=True)
            st.image(compressed_img, use_container_width=True)

        compressed_pil = Image.fromarray(compressed_img)

        if not os.path.exists("outputs"):
            os.makedirs("outputs")

        buffer = io.BytesIO()
        if output_format == "PNG":
            compressed_pil.save(buffer, format="PNG", optimize=True)
            extension, mime_type = "png", "image/png"
        elif output_format == "WEBP":
            compressed_pil.save(buffer, format="WEBP", quality=80)
            extension, mime_type = "webp", "image/webp"
        else:
            compressed_pil.save(buffer, format="JPEG", quality=70, optimize=True)
            extension, mime_type = "jpg", "image/jpeg"

        compressed_size = len(buffer.getvalue())
        uploaded_file.seek(0)
        original_size   = len(uploaded_file.read())
        ratio           = original_size / compressed_size if compressed_size > 0 else 0
        savings_pct     = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        with open(f"outputs/compressed.{extension}", "wb") as f:
            f.write(buffer.getvalue())

        st.success("✅  Compression complete! Your image is ready to download.")

        st.markdown('<p class="section-heading">05 — Statistics</p>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stat-grid">
          <div class="stat-card stat-original">
            <div class="stat-icon">📁</div>
            <p class="stat-value">{original_size/1024:.1f}<span style="font-size:.65em;font-weight:400;color:#94a3b8"> KB</span></p>
            <p class="stat-label">Original size</p>
          </div>
          <div class="stat-card stat-compressed">
            <div class="stat-icon">📦</div>
            <p class="stat-value">{compressed_size/1024:.1f}<span style="font-size:.65em;font-weight:400;color:#94a3b8"> KB</span></p>
            <p class="stat-label">Compressed size</p>
          </div>
          <div class="stat-card stat-ratio">
            <div class="stat-icon">🚀</div>
            <p class="stat-value">{savings_pct:.0f}<span style="font-size:.65em;font-weight:400;color:#94a3b8">%</span></p>
            <p class="stat-label">Space saved</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="⬇️  Download Compressed Image",
            data=buffer.getvalue(),
            file_name=f"compressed.{extension}",
            mime=mime_type
        )