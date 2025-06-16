# rag_pipeline.py
import os

from dotenv import load_dotenv

load_dotenv()


from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA



ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_KEYSPACE = os.environ.get("ASTRA_DB_KEYSPACE")
USER_AGENT = os.environ.get("USER_AGENT")
ASTRA_DB_API_KEY_NAME = os.environ.get("ASTRA_DB_API_KEY_NAME") or None
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or None


def load_combined_qa_chain():
    embeddings = OpenAIEmbeddings()

    retriever_fia = AstraDBVectorStore(
        collection_name="fia_documents",
        embedding=embeddings,
        token=ASTRA_DB_APPLICATION_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        namespace=ASTRA_DB_KEYSPACE,
    ).as_retriever(search_kwargs={"k": 5})

    retriever_news = AstraDBVectorStore(
        collection_name="f1_latest_news",
        embedding=embeddings,
        token=ASTRA_DB_APPLICATION_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        namespace=ASTRA_DB_KEYSPACE,
    ).as_retriever(search_kwargs={"k": 5})

    combined = EnsembleRetriever(retrievers=[retriever_fia, retriever_news])
    llm = ChatOpenAI(model_name="gpt-4.1")
    return RetrievalQA.from_chain_type(llm=llm, retriever=combined, return_source_documents=True)