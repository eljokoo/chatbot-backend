import asyncio
import pprint
from setup.ai_extractor import extract
from setup.schemas import SchemaPartSelect
from setup.scrape import ascrape_part_websites_links, ascrape_playwright

from langchain_dartmouth.embeddings import DartmouthEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
from dotenv import load_dotenv

load_dotenv()

# TESTING
if __name__ == "__main__":
    token_limit = 4000

    partselect_url = "https://www.partselect.com/PS11752778-Whirlpool-WPW10321304-Refrigerator-Door-Shelf-Bin.htm"
    partselect_fridge_url = "https://www.partselect.com/Refrigerator-Parts.htm"
    partselect_admiral_fridge_url = "https://www.partselect.com/Admiral-Refrigerator-Parts.htm"
    partselect_fridge_specifics_url = "https://www.partselect.com/Admiral-Refrigerator-Trays-and-Shelves.htm"
    partselect_general_url = "https://www.partselect.com/"

    collection_name = "extracted_content"

    async def scrape_with_playwright(url: str, tags, token_limit=4000, **kwargs):
        html_content, img = await ascrape_playwright(url, tags)

        print("Extracting content with LLM")

        html_content_fits_context_window_llm = html_content[:token_limit]

        extracted_content = extract(**kwargs, content=html_content_fits_context_window_llm)

        print("Extracted content: ", str(extracted_content))

        # Store the extracted content in a Chroma vectorstore
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=DartmouthEmbeddings(dartmouth_api_key=os.getenv('DARTMOUTH_API_KEY')),
            persist_directory="./chroma_db"
        )

        document = Document(page_content=str(extracted_content), metadata={"part_image_url": img})

        vectorstore.add_documents(documents=[document], ids=[extracted_content.partselect_number])
        print(f"Added extracted content to chroma vectorstore (collection: {collection_name})")

    asyncio.run(scrape_with_playwright(partselect_url, ["h1", "h2", "h3", "div", "img", "a"], schema=SchemaPartSelect))
