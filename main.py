from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from unstructured.partition.auto import partition
import requests
import tempfile
import os
import uvicorn
import ocrmypdf
import pymupdf4llm

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Health check endpoint
@app.get("/")
def health_check():
    return {"status": "ok"}

def extract_text_from_url(file_url: str) -> str:
    try:
        # if file type is pdf, use this
        file_extension = os.path.splitext(file_url)[-1].lower()
        if file_extension == ".pdf":
            response = requests.get(file_url)
            response.raise_for_status()
            temp_file_path = f"/tmp/temp_file{file_extension}"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(response.content)
            output_pdf_path = "/tmp/output_file.pdf"
            ocrmypdf.ocr(
                temp_file_path,
                output_pdf_path,
                skip_text=True,
                optimize=0,
                output_type="pdf",
                fast_web_view=999999,
                language="eng+ara"
            )
            extracted_text = pymupdf4llm.to_markdown(output_pdf_path)
        else:  # if any type other than pdf, use this
            elements = partition(url=file_url, languages=["eng", "ara"])
            extracted_text = "\n".join(str(element) for element in elements)
        return extracted_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

@app.post("/extract-text")
async def extract_text_from_url_endpoint(request_body: dict):
    file_url = request_body.get("file_url")
    if not file_url:
        raise HTTPException(status_code=400, detail="file_url is required in the request body")

    # Extract text directly from the remote file
    try:
        extracted_text = extract_text_from_url(file_url)
        return {"extracted_text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
