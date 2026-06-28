# 🤖 Cognitive RAG Compass

A production-grade, microservice-decoupled Retrieval-Augmented Generation (RAG) platform. This architecture leverages an asynchronous streaming ingestion engine to process massive document payloads securely without host memory degradation, alongside a localized vector database cluster for contextual text matching.

---

## 🚀 Live Architecture Links
* **Interactive Frontend Dashboard:** https://cognitive-rag-compassgit-wp4aa3y6s4kgymkvw2jvyj.streamlit.app/
* **Asynchronous Inference Backend:** https://pushkarini-rag-backend.hf.space

---

## ⚡ Core Engineering Challenges Solved (System Bottlenecks)

### 1. Memory Ingestion Boundaries (RAM Isolation)
* **The Problem:** Standard RAG pipelines ingest multi-megabyte PDF files completely into host memory (RAM) prior to serialization. Under concurrent usage loads, memory consumption scales linearly, triggering System Out-Of-Memory (OOM) fatal crashes.
* **The Solution:** Engineered an asynchronous, non-blocking stream-buffer pipeline utilizing FastAPI. File payloads are processed as sequential 1MB binary fragments, decoupling document size from server RAM profiles and holding operational memory flat under 50MB.

### 2. State-Cache Contamination (Session Isolation)
* **The Problem:** Multi-user environments risk context pollution inside shared vector indexes, where data blocks from previous file uploads mix into the proximity search space of independent queries.
* **The Solution:** Implemented a secure drop-and-recreate collections workflow. The vector vault completely drops database partitions and re-initializes fresh collections on every fresh file upload event, guaranteeing session-level boundary isolation.

### 3. Vector Proximity Hallucinations (Similarity Thresholding)
* **The Problem:** Standard vector store configurations return a fixed number of search results (`top_k`) even if the input text is conceptual gibberish, forcing the generation model to hallucinate false contexts.
* **The Solution:** Implemented strict mathematical Distance Boundary Filters checking Cosine Proximity angles. Slices exceeding a specific spatial threshold distance are dropped from the retrieval array, preventing out-of-bounds noise from contaminating the response.

---

## 🛠️ Technological Blueprints (The Stack)

* **Language Platform:** Python 3.10+
* **Asynchronous Web Infrastructure:** FastAPI + Uvicorn Async I/O Motor
* **Presentation Presentation Layer:** Streamlit Responsive Engine + Custom CSS 
* **Mathematical Storage Cluster:** Embedded ChromaDB Vector Engine (Persistent Engine)
* **Neural Vector Text Transformer:** Hugging Face `all-MiniLM-L6-v2` (Dense 384-dimensional space)
* **Deep Inference Core Machine:** DistilBERT-SQUAD Neural Model via PyTorch Tensor Math
* **Infrastructure Isolation Blueprint:** Linux Slim Container Environment via Dockerfile Configuration

---

## 📊 System Architecture Data Flow Chart

```text
[ Client Front-End UI Dashboard (Streamlit Cloud Cluster) ]
                           │
                           ▼ (Dispatches Async HTTP Streaming Payload)
[ Containerized Microservice Backend API (Hugging Face Spaces Core) ]
                           │
    ┌──────────────────────┴──────────────────────┐
    ▼ (Asynchronous 1MB Buffers to Disk)          ▼ (Calculates PyTorch Neural Coordinates)
[ Ephemeral Host File System ]               [ Microsoft MiniLM Vectorization Engine ]
    │                                             │
    ▼ (Sequentially Stripped Text Passages)       ▼ (Generates Concept Position Vectors)
[ PyPDF Structural Parsing Engine ] ----------> [ Embedded ChromaDB Vault Storage ]
                                                  │
                                                  ▼ (Applies Cosine Proximity Constraints)
                                            [ Filtered Semantic Slices Only ]
                                                  │
                                                  ▼ (Pure Tensor Index Matrix Slicing)
                                            [ DistilBERT QA Logic Inference ]
                                                  │
                                                  ▼ (Returns Exact Conceptual Match)
                                            [ Pure Short-form Chatbot Answer Result ]
```

---

## ⚙️ Local Development Setup

To replicate this environment sandbox locally on your machine, activate your terminal and run these procedural commands:

```bash
# 1. Clone the master workspace
git clone https://github.com
cd cognitive-rag-compass

# 2. Establish and boot the virtual runtime sandbox
python3 -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate

# 3. Compile required enterprise packages
pip install -r requirements.txt

# 4. Fire up the Core API Brain Motor
uvicorn app:app --reload --host localhost --port 8000

# 5. Open a parallel terminal panel and launch the Presentation UI
streamlit run ui.py
```
