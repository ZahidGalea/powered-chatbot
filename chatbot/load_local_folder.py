import core
from chatbot.pinecone_manager import PineconeClientManager


def load_local_folder(folder, index_name_to_load):
    pinecone_manager = PineconeClientManager()
    get_indexes_and_vstore = pinecone_manager.get_indexes_and_vstore()
    for indexes_tuples in get_indexes_and_vstore.values():
        index_name, index, vector_store = indexes_tuples
        if index_name == index_name_to_load:
            storage_context, service_context, token_counter = core.build_pre_index(
                vector_store=vector_store,
                llm_type="openai",
            )

            pinecone_manager.load_local_folder_to_pinecone(
                folder_path=folder,
                index_name=index_name,
                service_context=service_context,
                storage_context=storage_context,
            )


if __name__ == "__main__":
    load_local_folder(
        folder="data/",
        index_name_to_load="dataverse-docs",
    )
