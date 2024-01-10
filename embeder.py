import arxiv
import fitz
import pathlib
import sys
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.vectorstores import chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import PyPDF2


def download_arxiv_paper(arxiv_id):
    client = arxiv.Client()
    paper = next(client.results(arxiv.Search(id_list=[arxiv_id])))
    file_path = f"{arxiv_id}.pdf"  # Save in the current working directory
    paper.download_pdf(filename=file_path)
    return file_path

def pdf_to_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in range(reader.numPages):
            text.append(reader.getPage(page).extractText())
        return chr(12).join(text)

def write_text_to_file(text, file_path):
    pathlib.Path(file_path).write_bytes(text.encode())

# New function to load text from file and process it
def load_and_process_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_text(data)

    # Create a vector store from the document chunks
    vectorstore = chroma.Chroma.from_texts(texts=all_splits, embedding=GPT4AllEmbeddings())

    return vectorstore

def process_text_file(arxiv_id):
    pdf_path = f"./{arxiv_id}.pdf"
    text_path = f"{pdf_path}.txt"

    # Check if the PDF already exists
    if not os.path.exists(pdf_path):
        # Download the paper
        download_arxiv_paper(arxiv_id, pdf_path)

    # Check if the text file already exists
    if not os.path.exists(text_path):
        # Convert the PDF to text and write to a file
        text = pdf_to_text(pdf_path)
        write_text_to_file(text, text_path)

    # Load and process the text
    vectorstore = load_and_process_text(text_path)

    return vectorstore

app = FastAPI()

class ArxivPaperID(BaseModel):
    paper_id: str

class ArxivQuery(BaseModel):
    paper_id: str
    question: str

@app.get("/")
async def read_root():
    return {"message": "Welcome to the arXiv paper downloading API. Use POST to submit paper IDs."}

@app.post("/download-arxiv/")
async def download_arxiv_endpoint(paper: ArxivPaperID):
    paper_id = paper.paper_id
    file_path = f"{paper_id}.pdf"

    if not os.path.isfile(file_path):
        file_path = download_arxiv_paper(paper_id)

    return FileResponse(file_path, media_type='application/pdf', filename=file_path)

@app.post("/process-query/")
async def process_query_endpoint(query: ArxivQuery):
    paper_id = query.paper_id
    question = query.question

    # Process the text file (download if necessary)
    vectorstore = process_text_file(paper_id)

    # Perform a similarity search
    docs = vectorstore.similarity_search(question)

    # Prepare and return the results
    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get('source', 'Unknown')
        })

    return {"number_of_documents": len(docs), "documents": results}
    
