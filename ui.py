import streamlit as st
import requests

# 1. Premium Page Configuration
st.set_page_config(
    page_title="Cognitive RAG Compass",
    page_icon="🤖",
    layout="centered"
)

# 2. Injecting Custom CSS to force light mode and pastel tones
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
        color: #2D3748;
    }
    .header-container {
        text-align: center;
        padding: 30px 10px;
        background: linear-gradient(135deg, #EBF8FF 0%, #FAF5FF 100%);
        border-radius: 20px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(45deg, #4FD1C5, #9F7AEA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .sub-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        color: #718096;
        font-weight: 400;
    }
    .pastel-info-card {
        background-color: #EBF8FF;
        border-left: 5px solid #63B3ED;
        padding: 15px;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        color: #2B6CB0;
        margin-bottom: 25px;
    }
    div[data-testid="stFileUploader"] {
        background-color: #F7FAFC;
        border: 2px dashed #E2E8F0;
        border-radius: 12px;
        padding: 10px;
    }
    .loading-text {
        color: #B7791F;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Render Title Area
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Cognitive RAG Compass</h1>
        <p class="sub-title">production-grade document ingestion & semantic search architecture</p>
    </div>
""", unsafe_allow_html=True)

st.write("")

# 4. Data Ingestion UI Section
st.markdown("#### 📁 Step 1: Data Ingestion Pipeline")
st.markdown("""
    <div class="pastel-info-card">
        ✨ <b>Architecture Insight:</b> This module implements an asynchronous memory-isolated 
        streaming engine. Files are ingested in sequential 1MB buffers to keep host RAM completely flat.
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    label="Upload your technical reference manual or textbook (PDF format)",
    type=["pdf"]
)

if uploaded_file is not None:
    st.markdown('<p class="loading-text">⚡ Engaging stream buffers... Writing bytes sequentially to disk...</p>', unsafe_allow_html=True)
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
    
    try:
        backend_url = "https://pushkarini-rag-backend.hf.space/v1/document/upload"
        response = requests.post(backend_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"🎉 Ingestion Pipeline Successful! {result['message']}")
            
            # Metrics Dashboard
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style="background-color: #E6FFFA; border: 1px solid #81E6D9; padding: 15px; border-radius: 10px; text-align: center;">
                        <p style="margin:0; color:#234E52; font-size:0.85rem; font-weight:600;">ACTIVE TARGET DOCUMENT</p>
                        <h3 style="margin:5px 0 0 0; color:#2C7A7B; font-size:1.1rem;">{result['filename']}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                    <div style="background-color: #FAF5FF; border: 1px solid #D6BCFA; padding: 15px; border-radius: 10px; text-align: center;">
                        <p style="margin:0; color:#44337A; font-size:0.85rem; font-weight:600;">EXTRACTED SEMANTICS</p>
                        <h3 style="margin:5px 0 0 0; color:#6B46C1; font-size:1.4rem;">{result['total_chunks_extracted']} units</h3>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ The extraction backend encountered an error processing this block payload.")
            
    except Exception as e:
    st.exception(e)

# 5. Semantic Search UI Section
st.write("---")
st.markdown("#### 💬 Step 2: Semantic Knowledge Search")
st.caption("Ask questions in natural language. The AI searches by concepts and context instead of rigid keywords.")

# Dynamic Retrieval Count Slider
search_limit = st.slider(
    label="Select maximum context segments to retrieve:",
    min_value=1,
    max_value=10,
    value=3
)

user_query = st.text_input(
    label="Enter your exploration query here:",
    placeholder="e.g., What are the core architectural limits or protocols?"
)

if user_query:
    with st.spinner("🔍 Calculating query embeddings and traversing vector space..."):
        try:
            search_url = f"https://pushkarini-rag-backend.hf.space/v1/document/search?query={user_query}&limit={search_limit}"
            search_response = requests.get(search_url)
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                
                if search_data["results_found"] == 0:
                    st.warning("⚠️ No matching contextual blocks found. Try adjusting your phrasing.")
                else:
                    # RENDER THE DIRECT CHATBOT ANSWER
                    st.markdown("### 🤖 Direct Answer:")
                    st.info(search_data["direct_answer"])
                    
                    st.write("---")
                    st.markdown(f"✨ **Source Evidence Slices ({search_data['results_found']}):**")
                    
                    for match in search_data["matches"]:
                        clean_text = match['text'].replace("\n", " ")
                        card_html = f"""
<div style="background-color: #F7FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
<p style="margin: 0 0 10px 0; color: #4A5568; font-size: 0.95rem; line-height: 1.6;">{clean_text}</p>
<span style="background-color: #FAF5FF; color: #6B46C1; font-size: 0.75rem; font-weight: 600; padding: 4px 10px; border-radius: 20px; border: 1px solid #D6BCFA;">
📍 Page {match['page_number']}
</span>
</div>
"""
                        st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.error("❌ The query engine backend returned an operation error.")
        except Exception as e:
    st.exception(e)

