import json
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_astradb import AstraDBVectorStore

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE"]

def load_chunks_from_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return [Document(page_content=item["page_content"], metadata=item["metadata"]) for item in data]

def build_vectorstore():
    chunks = load_chunks_from_json("chunks/chunks.json")
    
    embeddings = OpenAIEmbeddings()  # Match dimension if needed
    
    vectorstore = AstraDBVectorStore(
        collection_name="fia_documents",
        embedding=embeddings,
        token=ASTRA_DB_APPLICATION_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        namespace=ASTRA_DB_KEYSPACE,
    )

    vectorstore.add_documents(chunks)
    print(f"✅ Uploaded {len(chunks)} chunks to AstraDB collection 'fia_documents'")

if __name__ == "__main__":
    build_vectorstore()
