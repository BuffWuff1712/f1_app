import os
import json
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_chunk_pdfs(folder_path):
    all_chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, filename))
            documents = loader.load()
            chunks = splitter.split_documents(documents)
            for chunk in chunks:
                chunk.metadata["source"] = filename
            all_chunks.extend(chunks)

    return all_chunks

def save_chunks_to_json(chunks, output_file):
    serialised = [
        {"page_content": c.page_content, "metadata": c.metadata}
        for c in chunks
    ]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serialised, f, indent=2)

if __name__ == "__main__":
    chunks = load_and_chunk_pdfs("data")
    save_chunks_to_json(chunks, "chunks/chunks.json")
    print(f"✅ Saved {len(chunks)} chunks to chunks/chunks.json")
