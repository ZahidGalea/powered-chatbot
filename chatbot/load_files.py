import os

import openai
from dotenv import load_dotenv
from llama_index import set_global_service_context

import common
from chromadb_client import ChromaDBClient

load_dotenv(override=True)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def load_local_folder(folder, chroma_collection_name):
    chromadb_client = ChromaDBClient()
    storage_context, service_context, vector_store = common.build_pre_index(
        _chroma_collection_name=chroma_collection_name,
        remote_db=chromadb_client.client,
        node_parser=common.get_node_parser(chunk_size=500, chunk_overlap=50),
        llm=common.get_llm(),
        embed_model=common.get_embedding_model(),
    )

    set_global_service_context(service_context)

    chromadb_client.load_local_folder_to_chromadb(
        folder_path=folder,
        collection_name=chroma_collection_name,
        service_context=service_context,
        storage_context=storage_context,
        delete_if_exists=True,
    )


if __name__ == "__main__":
    load_local_folder(
        folder="data/",
        chroma_collection_name=common.ChromaDBCollections.default_collection,
    )
