import logging
import os
from datetime import datetime

import pinecone
from llama_index import (
    GoogleDocsReader,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
TreeIndex
)
from llama_index.vector_stores import PineconeVectorStore



PINECONE_INDEXES = ["dataverse-docs"]


class PineconeClientManager:
    def __init__(self, key=None, environment=None, _type="http"):
        self.api_key = key or os.environ.get("PINECONE_API_KEY")
        assert self.api_key
        self.environment = environment or os.environ.get("PINECONE_ENVIRONMENT")
        assert self.environment
        self.pinecone_init()

    def pinecone_init(self, _type=None):
        logging.info("Initializing pinecone")
        pinecone.init(api_key=self.api_key, environment=self.environment)
        logging.info(f"Available indexes: {self.list_pinecone_indexes()}")

    def list_pinecone_indexes(self):
        return pinecone.list_indexes()

    def get_pinecone_index(self, index_name: str):
        return pinecone.Index(index_name)

    def create_pinecone_index(self, index_name: str, dimension, metadata_config: dict):
        return pinecone.create_index(
            index_name,
            dimension=dimension,
            metric="cosine",
            metadata_config={"company": "acidlabs", "support": "dataverse"}.update(
                metadata_config
            ),
        )

    def load_local_folder_to_pinecone(
        self,
        folder_path: str,
        index_name: str,
        service_context: ServiceContext,
        storage_context: StorageContext,
    ):
        filename_inclusion = lambda filename: {
            "file_name": filename,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        documents = SimpleDirectoryReader(
            input_dir=folder_path,
            filename_as_id=True,
            file_metadata=filename_inclusion,
        ).load_data()

        logging.info(f"Loading {len(documents)} documents to {index_name}")
        from chatbot.core import get_sentence_node_parser
        node_parser = get_sentence_node_parser()
        nodes = node_parser.get_nodes_from_documents(documents)

        
        vector_store_index = VectorStoreIndex.from_documents(
            documents=documents,
            service_context=service_context,
            storage_context=storage_context,
        )

    def load_google_doc_to_pinecone(
        self,
        documents_id: list,
        index_name: str,
        service_context: ServiceContext,
        storage_context: StorageContext,
    ):
        documents = GoogleDocsReader().load_data(document_ids=documents_id)
        logging.info(f"Loading {len(documents)} documents to {index_name}")
        result = VectorStoreIndex.from_documents(
            documents=documents,
            service_context=service_context,
            storage_context=storage_context,
        )

    def get_indexes_and_vstore(self):
        vector_stores = {}
        for index_name in PINECONE_INDEXES:
            index = self.get_pinecone_index(index_name=index_name)
            vector_store = PineconeVectorStore(
                pinecone_index=index, environment=self.environment
            )
            vector_stores[index_name] = (
                index_name,
                index,
                vector_store,
            )

        return vector_stores


if __name__ == "__main__":
    raise NotImplementedError
