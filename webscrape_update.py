# webscrape_update.py
import os
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from random import uniform

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_astradb import AstraDBVectorStore

load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
ASTRA_DB_KEYSPACE = os.environ.get("ASTRA_DB_KEYSPACE")
USER_AGENT = os.environ.get("USER_AGENT")

# Static and dynamic links combined
static_links = [
    "https://www.formula1.com/en/drivers.html",
    "https://www.formula1.com/en/teams.html",
    "https://www.formula1.com/en/drivers/hall-of-fame.html",
]

root_link = "https://www.formula1.com/en/results/2025"
dynamic_links = [
    f"{root_link}/drivers.html",
    f"{root_link}/team.html",
    f"{root_link}/races.html",
    f"{root_link}/fastest-laps.html",
    "https://www.formula1.com/en/racing/2025",  # race schedule
]

# Wikipedia + official news feed
other_sources = [
    "https://www.formula1.com/en/latest/all",
    "https://en.wikipedia.org/wiki/Formula_One",
    "https://en.wikipedia.org/wiki/List_of_Formula_One_Grand_Prix_winners",
    "https://en.wikipedia.org/wiki/List_of_Formula_One_World_Constructors%27_Champions",
    "https://en.wikipedia.org/wiki/List_of_Formula_One_circuits",
    "https://en.wikipedia.org/wiki/List_of_Formula_One_driver_records"
]

f1_updated_data = static_links + dynamic_links + other_sources

SCRAPE_METADATA_FILE = "last_scrape.json"

def should_scrape():
    if not os.path.exists(SCRAPE_METADATA_FILE):
        return True
    with open(SCRAPE_METADATA_FILE, "r") as f:
        last = datetime.fromisoformat(json.load(f)["last_scrape"])
    return datetime.now() - last > timedelta(days=0)

def update_scrape_timestamp():
    with open(SCRAPE_METADATA_FILE, "w") as f:
        json.dump({"last_scrape": datetime.now().isoformat()}, f)

def update_general_f1_news():
    all_split_docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)

    print("🔎 Loading from URLs (staggered):")
    for url in f1_updated_data:
        print(f"→ Scraping: {url}")
        try:
            loader = WebBaseLoader([url], header_template={"User-Agent": USER_AGENT})
            raw_documents = loader.load()

            split_docs = splitter.split_documents(raw_documents)
            for doc in split_docs:
                doc.metadata["source"] = url
            all_split_docs.extend(split_docs)

            wait_time = uniform(2.0, 4.0)  # wait between 2–4 seconds
            print(f"⏳ Waiting {wait_time:.1f}s before next request...\n")
            time.sleep(wait_time)

        except Exception as e:
            print(f"⚠️ Failed to scrape {url}: {e}")

    if not all_split_docs:
        print("❌ No documents were scraped. Aborting upload.")
        return

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    vector_store = AstraDBVectorStore(
        collection_name="f1_latest_news",
        embedding=embeddings,
        token=ASTRA_DB_APPLICATION_TOKEN,
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        namespace=ASTRA_DB_KEYSPACE,
    )
    vector_store.add_documents(all_split_docs)
    print(f"✅ Uploaded {len(all_split_docs)} chunks to 'f1_latest_news'")

if __name__ == "__main__":
    if should_scrape():
        print("🕒 Scraping new data...")
        update_general_f1_news()
        update_scrape_timestamp()
    else:
        print("⏳ Recent data already scraped. Skipping update.")
