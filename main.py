from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import arxiv
from pydantic import BaseModel
import requests

app = FastAPI()

# Define a model for the arXiv paper ID
class ArxivPaperID(BaseModel):
    paper_id: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the arXiv paper downloading API. Use POST to submit paper IDs."}

def download_arxiv_paper(arxiv_id: str, download_dir: str = "/mnt/mydisk/downloads") -> str:
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    file_path = os.path.join(download_dir, f"{arxiv_id}.pdf")
    
    if not os.path.isfile(file_path):
        paper = next(arxiv.Client().results(arxiv.Search(id_list=[arxiv_id])))
        # Download the paper as raw data
        response = requests.get(paper.pdf_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
        else:
            raise Exception("Failed to download paper")

    return file_path

@app.post("/download-arxiv/")
async def download_arxiv_endpoint(paper: ArxivPaperID):
    paper_id = paper.paper_id
    file_path = f"/mnt/mydisk/downloads/{paper_id}.pdf"  # Adjusted to use persistent storage

    if not os.path.isfile(file_path):
        file_path = download_arxiv_paper(paper_id, download_dir="/mnt/mydisk/downloads")

    return FileResponse(file_path, media_type='application/pdf', filename=f"{paper_id}.pdf")
