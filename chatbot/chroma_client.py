import datetime
import logging
import os

import chromadb
from chromadb import API
from llama_index import (
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)

from core import ChromaDBCollections


class ChromaDBClient:
    client: API

    def __init__(self, host=None, port=None, _type="http"):
        self.port = host or os.environ.get("CHROMADB_PORT", "8000")
        self.host = port or os.environ.get("CHROMADB_HOST", "host.docker.internal")
        self._type = _type
        self.set_chromadb_client()

    def set_chromadb_client(self, _type=None):
        if _type:
            self._type = _type
        if self._type == "http":
            self.client = chromadb.HttpClient(host=self.host, port=self.port)

    def query_chromadb(self, embedding_model, collection_name, str_to_query):
        embedding = embedding_model.get_text_embedding(str_to_query)
        self.client.get_collection(collection_name).query(query_embeddings=embedding)

    def load_local_folder_to_chromadb(
        self,
        folder_path: str,
        collection_name: str,
        service_context: ServiceContext,
        storage_context: StorageContext,
        delete_if_exists=True,
    ):
        collection = self.client.get_or_create_collection(collection_name)
        filename_inclusion = lambda filename: {
            "file_name": filename,
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        documents = SimpleDirectoryReader(
            input_dir=folder_path, filename_as_id=True, file_metadata=filename_inclusion
        ).load_data()

        if delete_if_exists:
            files_to_load = [doc.metadata["file_name"] for doc in documents]
            # Truncate first then load again
            for file in files_to_load:
                logging.info(f"Deleting file {file} from {collection_name} if exists")
                collection.delete(where={"file_name": file})
        logging.info(f"Loading {len(documents)} documents to {collection_name}")
        result = VectorStoreIndex.from_documents(
            documents=documents,
            service_context=service_context,
            storage_context=storage_context,
        )

    def list_collections(self):
        return self.client.list_collections()

    def list_files_loaded_per_collection(self):
        collections = self.client.list_collections()
        files_loaded = []
        already_in = []
        for collection in collections:
            col_data = collection.get()
            metadatas = col_data["metadatas"]
            for metadata in metadatas:
                if "file_name" in metadata:
                    if not metadata["file_name"] in already_in:
                        already_in.append(metadata["file_name"])
                        files_loaded.append(
                            (metadata["file_name"], metadata["datetime"])
                        )
        return files_loaded


if __name__ == "__main__":
    client = ChromaDBClient()
    collections = client.list_files_loaded_per_collection()
    print(client.client.get_collection(ChromaDBCollections.default_collection))
