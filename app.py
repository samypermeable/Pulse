import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import time
import plotly.express as px
import plotly.graph_objects as go

# --- Helper Function: Safe Application Rerun ---
def force_rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# --- Page Configuration ---
st.set_page_config(page_title="Team Pulse | PSR Enhancer", layout="wide")

# --- Custom CSS Stylesheet & Theme Configuration ---
base_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stAppDeployButton {display:none;}

h1 a, h2 a, h3 a, h4 a, h5 a, h6 a, .stMarkdown a { display: none !important; }

/* --- Universal Cross-Platform Twinkling Space Background --- */
.stApp {
    background-color: #000000;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-image: 
        radial-gradient(1px 1px at 20px 30px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 150px 80px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 300px 150px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 450px 200px, rgba(255,255,255,0.8), rgba(0,0,0,0)),
        radial-gradient(1px 1px at 100px 350px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 250px 450px, rgba(255,255,255,0.9), rgba(0,0,0,0)),
        radial-gradient(1px 1px at 500px 500px, #ffffff, rgba(0,0,0,0));
    background-repeat: repeat;
    background-size: 550px 550px;
    z-index: 0;
    pointer-events: none;
    -webkit-transform: translateZ(0);
    transform: translateZ(0);
    -webkit-animation: starTwinkle 6s infinite ease-in-out;
    animation: starTwinkle 6s infinite ease-in-out;
}

@-webkit-keyframes starTwinkle {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

@keyframes starTwinkle {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

.main {
    z-index: 1;
}

/* Typography Styles */
h1, h2, h3, h4 { color: #ffffff !important; font-weight: 500 !important; letter-spacing: -0.5px; }
p, span, label, .stMarkdown, .stMetricValue { color: #cccccc !important; font-weight: 300 !important; }

/* Branding Styles */
.team-pulse-header {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    text-transform: uppercase !important;
    color: #ffffff !important;
    text-align: center !important;
    margin-bottom: 0px !important;
}
.team-pulse-highlight {
    color: #00F0FF !important;
    font-weight: 900 !important;
    text-shadow: 0 0 15px rgba(0,240,255,0.8) !important;
}

/* --- Smooth Transition Animations --- */
@keyframes glassReveal {
    0% { opacity: 0; transform: translateY(30px); filter: blur(12px); }
    100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
}

.fade-in {
    animation: glassReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

[data-testid="stTabs"], [data-testid="stImage"], [data-testid="stPlotlyChart"], [data-testid="stMetric"], [data-testid="stDownloadButton"], [data-testid="stFileUploader"] {
    animation: glassReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* --- Scanner Animation Styles --- */
.scanner-container {
    width: 100%;
    background: rgba(0, 240, 255, 0.02);
    border: 1px solid rgba(0, 240, 255, 0.15);
    border-radius: 10px;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: inset 0 0 40px rgba(0, 240, 255, 0.05);
    animation: glassReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.scanner-line {
    position: absolute;
    top: 0; left: 0; width: 100%; height: 3px; background: #00F0FF;
    box-shadow: 0 0 15px #00F0FF, 0 0 40px #00F0FF;
    animation: scan 2s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
}
@keyframes scan { 0% { top: 0%; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
.scanner-text {
    font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.2rem; letter-spacing: 4px;
    color: #ffffff; text-shadow: 0 0 15px rgba(0, 240, 255, 0.8); z-index: 10;
    animation: pulse-text 1.5s infinite; text-align: center;
}
@keyframes pulse-text { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; text-shadow: 0 0 25px rgba(0, 240, 255, 1); } }

/* --- Component Overrides --- */
div[role="tablist"] { justify-content: center !important; gap: 30px; }
[data-testid="stTabs"] button { background-color: transparent !important; font-size: 1.1rem !important; }

[data-testid="stMetric"] { display: flex !important; flex-direction: column !important; align-items: center !important; text-align: center !important; width: 100% !important; }
[data-testid="stMetricLabel"] { display: flex !important; justify-content: center !important; width: 100% !important; }
[data-testid="stMetricValue"] { display: flex !important; justify-content: center !important; width: 100% !important; }
[data-testid="stMetricDelta"] { display: flex !important; justify-content: center !important; width: 100% !important; }
[data-testid="stMetricDelta"] > div { display: flex !important; justify-content: center !important; align-items: center !important; }

.stButton>button, .stDownloadButton>button {
    background-color: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(15px) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important; color: #ffffff !important;
    border-radius: 30px !important; padding: 12px 35px !important; font-weight: 400 !important; transition: all 0.3s ease;
}
.stButton>button:hover, .stDownloadButton>button:hover {
    background-color: rgba(255, 255, 255, 0.15) !important; border: 1px solid #00F0FF !important; transform: translateY(-2px);
}

.center-text { text-align: center; }
hr { border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-top: 2rem; margin-bottom: 2rem; }
</style>
"""
st.markdown(base_css, unsafe_allow_html=True)

# --- Application Header ---
st.markdown("""
    <div class="fade-in" style="text-align: center; margin-bottom: 0px;">
        <p class="team-pulse-header">
            DEVELOPED BY TEAM <span class="team-pulse-highlight">PULSE</span>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="fade-in" style="text-align: center; font-family: 'Poppins', sans-serif; font-weight: 800; font-size: 3.2rem; color: #ffffff; letter-spacing: -2px; margin-top: 5px; margin-bottom: 5px;">
        Lunar PSR Image Enhancer
    </div>
""", unsafe_allow_html=True)
st.markdown("<p class='center-text fade-in' style='color: rgba(255, 255, 255, 0.7) !important; font-size: 1rem; font-weight: 400 !important;'>Enhancement of Permanently Shadowed Regions (PSR) of Lunar Craters Captured by OHRC of Chandrayaan-2</p>", unsafe_allow_html=True)
st.divider()

# --- Processing Parameters ---
CLIP_LIMIT = 3.0
GAMMA = 1.2

# --- Helper Function: Entropy Calculation ---
def calculate_entropy(img):
    hist = cv2.calcHist([img], [0], None, [256], [0, 256]).ravel()
    hist = hist[hist > 0] / hist.sum()
    return -np.sum(hist * np.log2(hist))

# --- Helper Function: Metrics & Download Button ---
def render_metrics_and_dl(img_array, processed_img, crater_data, key_suffix):
    st.divider()
    m1, m2, m3 = st.columns(3)
    raw_lum = np.mean(img_array)
    enh_lum = np.mean(processed_img)
    raw_ent = calculate_entropy(img_array)
    enh_ent = calculate_entropy(processed_img)
    
    with m1: st.metric("Image Brightness", f"{enh_lum:.2f}", delta=f"{enh_lum - raw_lum:.2f}")
    with m2: st.metric("Detail Score (Entropy)", f"{enh_ent:.2f}", delta=f"{enh_ent - raw_ent:.2f}")
    with m3: st.metric("Hazards / Craters Found", len(crater_data), delta="Tracking Active")

    st.write("") 
    dl_col1, dl_col2, dl_col3 = st.columns([1, 1.5, 1])
    with dl_col2:
        is_success, buffer = cv2.imencode(".png", processed_img)
        if is_success:
            st.download_button(label="Download Enhanced Image", data=io.BytesIO(buffer), file_name="enhanced_lunar_image.png", mime="image/png", use_container_width=True, key=f"dl_{key_suffix}")

# --- Session State Management ---
if 'image_bytes' not in st.session_state:
    st.session_state.image_bytes = None
if 'has_processed' not in st.session_state:
    st.session_state.has_processed = False

# --- View 1: Initial Image Upload Screen ---
if st.session_state.image_bytes is None:
    direct_uploader_css = """
    <style>
    [data-testid="stFileUploader"] label { display: flex !important; justify-content: center !important; width: 100% !important; padding-bottom: 15px !important; }
    
    [data-testid="stFileUploadDropzone"], 
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 30px !important; 
        padding: 50px 30px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        cursor: pointer !important;
        position: relative !important;
        display: flex !important; 
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 180px !important;
        animation: glassReveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    [data-testid="stFileUploadDropzone"]:hover, 
    [data-testid="stFileUploaderDropzone"]:hover {
        background: rgba(255, 255, 255, 0.07) !important;
        border-color: #00F0FF !important;
        transform: translateY(-3px) scale(1.01) !important;
        box-shadow: 0 20px 40px rgba(0, 240, 255, 0.15) !important;
    }
    
    [data-testid="stFileUploadDropzone"] *, 
    [data-testid="stFileUploaderDropzone"] * {
        display: none !important;
    }
    
    [data-testid="stFileUploadDropzone"]::after,
    [data-testid="stFileUploaderDropzone"]::after {
        content: "Drag & Drop or Click to Upload (PNG, JPG)" !important;
        color: #ffffff !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        height: 100% !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        pointer-events: none !important;
    }
    </style>
    """
    st.markdown(direct_uploader_css, unsafe_allow_html=True)
    
    up_col1, up_col2, up_col3 = st.columns([1, 1.5, 1])
    with up_col2:
        file = st.file_uploader("Upload Lunar Image", type=["png", "jpg", "jpeg"], key="main_upload")
        if file is not None:
            st.session_state.image_bytes = file.getvalue()
            st.session_state.has_processed = False
            force_rerun()

# --- View 2: Multi-Tab Dashboard Interface ---
else:
    image = Image.open(io.BytesIO(st.session_state.image_bytes)).convert("L")
    img_array = np.array(image)
    img_height, img_width = img_array.shape
    
    tab1, tab2, tab3, tab4 = st.tabs(["Image Enhancement", "Crater & Hazard Detection", "3D Map & Safe Landing", "Upload New Image"])
    
    # Tab 4: Reset Interface
    with tab4:
        st.markdown("<br><br><h4 class='center-text fade-in'>Ready for a new analysis?</h4><br>", unsafe_allow_html=True)
        btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1])
        with btn_col2:
            if st.button("Reset & Upload New Image", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                force_rerun()

    # --- Pre-calculate all Image Data Before Rendering UI ---
    
    # 1. Image Processing (For Human Eyes & 3D Map)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=(8, 8))
    base_img = clahe.apply(img_array.copy())
    invGamma = 1.0 / GAMMA
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in range(256)]).astype("uint8")
    base_img = cv2.LUT(base_img, table)
    gaussian_blur_sharp = cv2.GaussianBlur(base_img, (5, 5), 1.0)
    processed_img = cv2.addWeighted(base_img, 1.5, gaussian_blur_sharp, -0.5, 0)
    
    # 2. CRATER DETECTION LOGIC (PRECISION SEPARATION FIX)
    detect_blur = cv2.GaussianBlur(processed_img, (7, 7), 0)
    _, thresh_craters = cv2.threshold(detect_blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Clean separation: Open to break bridges between craters, small Close to fill internal noise
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    thresh_craters = cv2.morphologyEx(thresh_craters, cv2.MORPH_OPEN, kernel_open, iterations=1)
    thresh_craters = cv2.morphologyEx(thresh_craters, cv2.MORPH_CLOSE, kernel_close, iterations=1)
    
    contours, _ = cv2.findContours(thresh_craters, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    crater_data = []
    total_pixels = img_width * img_height
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Strict upper limit (15%) prevents massive overlapping mega-boxes
        if 180 < area < (total_pixels * 0.15): 
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / float(h)
            
            # Clean square/oval aspect ratio limits
            if 0.4 <= aspect_ratio <= 2.5:
                perimeter = cv2.arcLength(cnt, True)
                circ = 0.0 if perimeter == 0 else 4 * np.pi * (area / (perimeter * perimeter))
                crater_data.append({"x": x, "y": y, "w": w, "h": h, "area": int(area), "circ": round(circ, 2)})

    # Keep the top 35 sharpest distinct craters
    crater_data = sorted(crater_data, key=lambda c: c['area'], reverse=True)[:35]

    # --- Animation Flow Control ---
    if not st.session_state.has_processed:
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h4 class='center-text fade-in'>Original Dark Image</h4>", unsafe_allow_html=True)
                st.image(img_array, use_container_width=True)
            with col2:
                st.markdown("<h4 class='center-text fade-in'>Enhanced Image</h4>", unsafe_allow_html=True)
                scanner_html = f"""
                <div class="scanner-container" style="aspect-ratio: {img_width} / {img_height};">
                    <div class="scanner-line"></div>
                    <div class="scanner-text">ENHANCING<br>LUNAR DATA...</div>
                </div>
                """
                st.markdown(scanner_html, unsafe_allow_html=True)
        with tab2:
            crater_html = f"""
            <br><br>
            <div class="scanner-container" style="aspect-ratio: {img_width} / {img_height}; width: 80%; margin: 0 auto;">
                <div class="scanner-line" style="animation-duration: 2.5s;"></div>
                <div class="scanner-text">MAPPING CRATERS...</div>
            </div>
            """
            st.markdown(crater_html, unsafe_allow_html=True)
            
        time.sleep(3)
        st.session_state.has_processed = True
        force_rerun()

    # --- Render Final Results ---
    else:
        # Tab 1: Enhancement
        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<h4 class='center-text fade-in'>Original Dark Image</h4>", unsafe_allow_html=True)
                st.image(img_array, use_container_width=True)
                
            with col2:
                st.markdown("<h4 class='center-text fade-in'>Enhanced Image</h4>", unsafe_allow_html=True)
                st.image(processed_img, use_container_width=True)
                
            render_metrics_and_dl(img_array, processed_img, crater_data, "tab1")

        # Tab 2: Crater Detection
        with tab2:
            st.markdown("<h4 class='center-text fade-in'>Automated Crater Detection</h4>", unsafe_allow_html=True)
            st.markdown("<p class='center-text fade-in'>Hover over the highlighted areas to view the size and circularity of the detected craters.</p>", unsafe_allow_html=True)
            
            img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)
            fig = px.imshow(img_rgb)
            for c in crater_data:
                fig.add_shape(type="rect", x0=c['x'], y0=c['y'], x1=c['x']+c['w'], y1=c['y']+c['h'], line=dict(color="#00F0FF", width=2.5))
                fig.add_trace(go.Scatter(x=[c['x'] + c['w']/2], y=[c['y'] + c['h']/2], mode="markers", marker=dict(color="rgba(0,0,0,0)", size=40), text=[f"<b>CRATER DETECTED</b><br>Size (Area): {c['area']} px²<br>Circularity: {c['circ']}"], hoverinfo="text", showlegend=False))
            
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            
            fig.update_layout(
                height=750, 
                margin=dict(l=0, r=0, t=0, b=0), 
                hovermode="closest", 
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(scaleanchor="y", scaleratio=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            render_metrics_and_dl(img_array, processed_img, crater_data, "tab2")

        # Tab 3: 3D Map & Safe Landing
        with tab3:
            st.markdown("<h4 class='center-text fade-in'>3D Lunar Surface & Safe Landing Zones</h4>", unsafe_allow_html=True)
            
            col_3d_1, col_3d_2 = st.columns(2)
            
            with col_3d_1:
                # 3D MAP FIX: Added heavy GaussianBlur so the terrain renders smooth, not spiky.
                smoothed_for_3d = cv2.GaussianBlur(processed_img, (15, 15), 0)
                scale_percent = 25 
                width = int(smoothed_for_3d.shape[1] * scale_percent / 100)
                height = int(smoothed_for_3d.shape[0] * scale_percent / 100)
                dim = (width, height)
                resized_img = cv2.resize(smoothed_for_3d, dim, interpolation=cv2.INTER_AREA)
                
                inverted_img = 255 - resized_img
                
                fig_3d = go.Figure(data=[go.Surface(z=inverted_img, colorscale='IceFire')])
                fig_3d.update_layout(
                    title='Interactive 3D Terrain Map',
                    autosize=True,
                    margin=dict(l=0, r=0, b=0, t=40),
                    scene=dict(
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        zaxis=dict(title='Depth', showgrid=False)
                    ),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white")
                )
                st.plotly_chart(fig_3d, use_container_width=True)

            with col_3d_2:
                # Safe Landing Map remains untouched because it works perfectly.
                smooth_for_sobel = cv2.GaussianBlur(processed_img, (15, 15), 0)
                
                sobelx = cv2.Sobel(smooth_for_sobel, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(smooth_for_sobel, cv2.CV_64F, 0, 1, ksize=3)
                gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
                
                gradient_normalized = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
                
                _, slope_hazard = cv2.threshold(gradient_normalized, 45, 255, cv2.THRESH_BINARY)
                _, dark_hazard = cv2.threshold(smooth_for_sobel, 50, 255, cv2.THRESH_BINARY_INV)
                
                hazard_mask = cv2.bitwise_or(slope_hazard, dark_hazard)
                safe_mask = cv2.bitwise_not(hazard_mask)
                
                overlay = np.zeros((img_height, img_width, 3), dtype=np.uint8)
                overlay[safe_mask == 255] = [0, 255, 0]   
                overlay[hazard_mask == 255] = [255, 0, 0] 
                
                img_color = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)
                landing_map = cv2.addWeighted(img_color, 0.6, overlay, 0.4, 0)
                
                st.markdown("<p style='text-align: center; color: white; font-weight: bold;'>Rover Safe Landing Map</p>", unsafe_allow_html=True)
                st.image(landing_map, use_container_width=True, caption="Green: Safe Flat Ground | Red: Crater Floors & Steep Rims")
