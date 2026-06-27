import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
app = FastAPI(
    title="Distributed RAG Platform",
    description="Production-grade document ingestion and semantic search engine.",
    version="1.0.0"
)
# Ensure a secure directory exists for temporary storage
UPLOAD_DIR = "./storage_vault"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 1MB chunk size buffer for controlled streaming
CHUNK_SIZE_BYTES = 1024 * 1024 
@app.post("/v1/document/upload")
async def upload_massive_document(file: UploadFile = File(...)):
    """
    Ingests files using a stream buffer and immediately extracts structured text chunks.
    """
    if not file.filename.endswith('.pdf'):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only PDF documents are supported."
        )
    
    target_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Stream the file chunk by chunk to disk (keeps RAM safe)
        with open(target_path, "wb") as buffer:
            while True:
                chunk = await file.read(CHUNK_SIZE_BYTES)
                if not chunk:
                    break
                buffer.write(chunk)
                
        # NEW CODE: Immediately parse the saved PDF file into structured paragraphs
        extracted_chunks = extract_text_chunks_from_pdf(target_path)
        
        return {
            "status": "success",
            "filename": file.filename,
            "total_chunks_extracted": len(extracted_chunks),
            "sample_chunk": extracted_chunks[0] if extracted_chunks else "No textual data found.",
            "message": "File streamed and parsed into semantic blocks successfully."
        }
        
    except Exception as e:
        if os.path.exists(target_path):
            os.remove(target_path)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline failed: {str(e)}"
        )

        
def extract_text_chunks_from_pdf(pdf_path: str):
    """
    Opens a saved PDF file, extracts raw human-readable text page-by-page, 
    and breaks it down into bite-sized, structured paragraphs (chunks).
    """
    from pypdf import PdfReader
    
    # 1. Open the PDF file handle using our new tool
    reader = PdfReader(pdf_path)
    all_chunks = []
    
    # 2. Loop through every single page in the document sequentially
    for page_num, page in enumerate(reader.pages):
        # Extract clean text from the current page
        page_text = page.extract_text()
        
        # If the page is empty (like an image or a blank layout), skip it
        if not page_text:
            continue
            
        # 3. Split the page text into individual paragraphs using double newlines
        paragraphs = page_text.split("\n\n")
        
        for paragraph in paragraphs:
            clean_paragraph = paragraph.strip()
            # Only save chunks that contain real textual information
            if len(clean_paragraph) > 20: 
                # Create a structured dictionary holding the text and its origin page
                chunk_data = {
                    "text": clean_paragraph,
                    "metadata": {
                        "source": pdf_path,
                        "page_number": page_num + 1 # Pages start at 0 internally, so we add 1
                    }
                }
                all_chunks.append(chunk_data)
                
    return all_chunks
