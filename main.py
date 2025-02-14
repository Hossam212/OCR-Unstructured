from fastapi import FastAPI, HTTPException
from unstructured.partition.auto import partition
import requests
import tempfile
import os

app = FastAPI()

def download_file(url: str) -> str:
    """
    Downloads a file from a public URL and saves it to a temporary file.
    Returns the path to the downloaded file.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download file: {str(e)}")

def extract_text(file_path: str) -> str:
    """
    Extracts text from a file using the `unstructured` library.
    """
    try:
        elements = partition(filename=file_path, languages=["eng", "ara"])
        extracted_text = "\n".join(str(element) for element in elements)
        return extracted_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")

@app.post("/extract-text")
async def extract_text_from_url(request_body: dict):
    """
    API endpoint to extract text from a file URL.
    Expects a JSON body with a "file_url" key.
    """
    file_url = request_body.get("file_url")
    if not file_url:
        raise HTTPException(status_code=400, detail="file_url is required in the request body")

    # Download the file
    file_path = download_file(file_url)

    # Extract text
    try:
        extracted_text = extract_text(file_path)
        return {"extracted_text": extracted_text}
    finally:
        # Clean up the temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

# Run the app with: uvicorn script_name:app --reload