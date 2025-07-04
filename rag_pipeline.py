# rag_pipeline.py
import os
import streamlit as st

from dotenv import load_dotenv

load_dotenv()


from langchain_astradb import AstraDBVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.retrievers import EnsembleRetriever
from langchain.chains import RetrievalQA


def get_config(key: str, default: str = None) -> str:
    return (
        os.environ.get(key) or
        st.secrets.get(key) or
        default
    )

ASTRA_DB_APPLICATION_TOKEN = get_config("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = get_config("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_KEYSPACE = get_config("ASTRA_DB_KEYSPACE")
USER_AGENT = get_config("USER_AGENT")
OPENAI_API_KEY = get_config("OPENAI_API_KEY")


def load_combined_qa_chain():
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

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