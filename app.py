import os
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions
from transformers import AutoModelForQuestionAnswering, AutoTokenizer

app = FastAPI(
    title="Cognitive RAG Compass",
    description="Production-grade document ingestion and semantic search engine.",
    version="1.0.0"
)

UPLOAD_DIR = "./storage_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)
CHUNK_SIZE_BYTES = 1024 * 1024 

# Initialize Database and Vector Embeddings
chroma_client = chromadb.PersistentClient(path="./.chroma_db")
ai_embedding_engine = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

vector_vault = chroma_client.get_or_create_collection(
    name="document_knowledge_matrix",
    embedding_function=ai_embedding_engine
)

# Initialize the explicit Question-Answering Model and Tokenizer
MODEL_NAME = "distilbert-base-cased-distilled-squad"
qa_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
qa_model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)

def extract_text_chunks_from_pdf(pdf_path: str):
    """Parses PDF page-by-page and yields clean paragraph structures."""
    reader = PdfReader(pdf_path)
    all_chunks = []
    
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if not page_text:
            continue
        paragraphs = page_text.split("\n\n")
        for paragraph in paragraphs:
            clean_paragraph = paragraph.strip()
            if len(clean_paragraph) > 5: 
                chunk_data = {
                    "text": clean_paragraph,
                    "source": pdf_path,
                    "page_number": page_num + 1
                }
                all_chunks.append(chunk_data)
    return all_chunks

@app.post("/v1/document/upload")
async def upload_massive_document(file: UploadFile = File(...)):
    """Streams data to disk, resets the vector collection, and handles fresh indexing."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")
    
    target_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        with open(target_path, "wb") as buffer:
            while True:
                chunk = await file.read(CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                buffer.write(chunk)
                
        extracted_chunks = extract_text_chunks_from_pdf(target_path)
        
        global vector_vault
        try:
            chroma_client.delete_collection(name="document_knowledge_matrix")
        except Exception:
            pass
            
        vector_vault = chroma_client.get_or_create_collection(
            name="document_knowledge_matrix",
            embedding_function=ai_embedding_engine
        )
        
        if extracted_chunks:
            documents_list = [c["text"] for c in extracted_chunks]
            metadatas_list = [{"source": c["source"], "page": c["page_number"]} for c in extracted_chunks]
            ids_list = [f"{file.filename}_chunk_{i}" for i in range(len(extracted_chunks))]
            
            vector_vault.upsert(
                ids=ids_list,
                documents=documents_list,
                metadatas=metadatas_list
            )
        
        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks_extracted": len(extracted_chunks),
            "message": "File streamed and vectorized inside ChromaDB database completely."
        }
        
    except Exception as e:
        if os.path.exists(target_path):
            os.remove(target_path)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")

@app.get("/v1/document/search")
async def search_document_knowledge(query: str, limit: int = 3):
    """Executes a search, drops irrelevant data, and calculates an answer using raw PyTorch tensors."""
    try:
        search_results = vector_vault.query(
            query_texts=[query],
            n_results=limit
        )
        
        formatted_matches = []
        combined_context_text = ""
        
        if search_results and search_results["documents"] and len(search_results["documents"]) > 0:
            docs = search_results["documents"][0]
            metas = search_results["metadatas"][0]
            distances = search_results["distances"][0]
            
            MAX_ALLOWABLE_DISTANCE = 1.3
            
            for i in range(len(docs)):
                if distances[i] > MAX_ALLOWABLE_DISTANCE:
                    continue
                    
                formatted_matches.append({
                    "text": docs[i],
                    "source": metas[i].get("source", "Unknown"),
                    "page_number": metas[i].get("page", "Unknown")
                })
                combined_context_text += docs[i] + " "
                
        direct_ai_answer = "No matching information found to answer this query safely."
        if formatted_matches and len(combined_context_text.strip()) > 10:
            try:
                inputs = qa_tokenizer(query, combined_context_text, add_special_tokens=True, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = qa_model(**inputs)
                    
                answer_start = torch.argmax(outputs.start_logits)
                answer_end = torch.argmax(outputs.end_logits) + 1
                
                # SQUEEZE FIX: Strips away the outer batch layer completely to avoid indexing mismatch crashes
                flat_input_ids = inputs["input_ids"].squeeze(0)
                answer_tokens = flat_input_ids[answer_start:answer_end]
                direct_ai_answer = qa_tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()
                
                if not direct_ai_answer or direct_ai_answer == "":
                    direct_ai_answer = formatted_matches[0]["text"]
            except Exception:
                # SAFE FAILSAFE: If the tensor math hits an edge case, return the direct extracted paragraph text
                direct_ai_answer = formatted_matches[0]["text"]
                
        return {
            "query": query,
            "results_found": len(formatted_matches),
            "direct_answer": direct_ai_answer,
            "matches": formatted_matches
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search vector failure: {str(e)}")
