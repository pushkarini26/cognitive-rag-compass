import streamlit as st
import requests

# 1. Premium Page Configuration
st.set_page_config(
    page_title="Enterprise Cognitive RAG",
    page_icon="🤖",
    layout="centered"
)

# 2. Injecting Custom CSS to force a crisp light mode, pastel tones, and stylish fonts
st.markdown("""
    <style>
    /* Force crisp white background for the entire application */
    .stApp {
        background-color: #FFFFFF;
        color: #2D3748;
    }
    
    /* Styled Title & Subtitle Container (Centered Layout) */
    .header-container {
        text-align: center;
        padding: 30px 10px;
        background: linear-gradient(135deg, #EBF8FF 0%, #FAF5FF 100%);
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .main-title {
        font-family: 'Playfair Display', 'Didot', 'Georgia', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #4FD1C5, #9F7AEA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .sub-title {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        font-size: 1.1rem;
        color: #718096;
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Elegant Pastel Information Cards */
    .pastel-info-card {
        background-color: #EBF8FF; /* Pastel Blue */
        border-left: 5px solid #63B3ED;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #2B6CB0;
        margin-bottom: 25px;
    }
    
    /* Custom Styling for Streamlit Upload Box Wrapper */
    div[data-testid="stFileUploader"] {
        background-color: #F7FAFC;
        border: 2px dashed #E2E8F0;
        border-radius: 12px;
        padding: 10px;
    }
    
    /* Smooth CSS animations for dynamic loading states */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-text {
        color: #B7791F;
        font-weight: 500;
        animation: pulse 1.5s infinite;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Render the Centered Styled Header Area
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Cognitive RAG Compass</h1>
        <p class="sub-title">production-grade document ingestion & semantic search architecture</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# 4. Dynamic Pipeline Section with Pastel Blue Card
st.markdown("#### 📁 Step 1: Data Ingestion Pipeline")
st.markdown("""
    <div class="pastel-info-card">
        ✨ <b>Architecture Insight:</b> This module implements an asynchronous memory-isolated 
        streaming engine. Files are ingested in sequential 1MB buffers to keep host RAM completely flat.
    </div>
""", unsafe_allow_html=True)

# 5. Drag-and-Drop Ingestion Component
uploaded_file = st.file_uploader(
    label="Upload your technical reference manual or textbook (PDF format)",
    type=["pdf"],
    label_visibility="visible"
)

# 6. Action Execution Loop
if uploaded_file is not None:
    # Custom styled spinner text matching the theme
    st.markdown('<p class="loading-text">⚡ Engaging stream buffers... Writing bytes sequentially to disk...</p>', unsafe_allow_html=True)
    
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    
    try:
        # Fire network call to our running FastAPI backend
        backend_url = "http://localhost:8000/v1/document/upload"

        response = requests.post(backend_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            
            # Celebratory visual confetti
            st.balloons()
            
            # Success Alert Box with soft background
            st.success(f"🎉 Ingestion Pipeline Successful! {result['message']}")
            
            # Render a Beautiful Layout Dashboard for Performance Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                    <div style="background-color: #E6FFFA; border: 1px solid #81E6D9; padding: 15px; border-radius: 10px; text-align: center;">
                        <p style="margin:0; color:#234E52; font-size:0.85rem; font-weight:600; text-transform: uppercase;">Active Target Document</p>
                        <h3 style="margin:5px 0 0 0; color:#2C7A7B; font-size:1.1rem;">{}</h3>
                    </div>
                """.format(result['filename']), unsafe_allow_html=True)
                
            with col2:
                st.markdown("""
                    <div style="background-color: #FAF5FF; border: 1px solid #D6BCFA; padding: 15px; border-radius: 10px; text-align: center;">
                        <p style="margin:0; color:#44337A; font-size:0.85rem; font-weight:600; text-transform: uppercase;">Extracted Semantics</p>
                        <h3 style="margin:5px 0 0 0; color:#6B46C1; font-size:1.4rem;">{} units</h3>
                    </div>
                """.format(result['total_chunks_extracted']), unsafe_allow_html=True)
            
            st.write("")
            
            # Pastel Accordion to peek at the underlying data structure
            with st.expander("🔍 Inspect Extracted Context Samples (Structured Matrix)"):
                st.write(result['sample_chunk'])
                
        else:
            st.error("❌ The extraction backend encountered an error processing this block payload.")
            
    except requests.exceptions.ConnectionError:
        st.markdown("""
            <div style="background-color: #FFF5F5; border-left: 5px solid #FEB2B2; padding: 15px; border-radius: 8px; color: #9B2C2C;">
                <b>❌ Network Connection Failure:</b> Unable to broadcast to the core engine. 
                Please verify that your FastAPI backend server is actively running on port 8000.
            </div>
        """, unsafe_allow_html=True)
