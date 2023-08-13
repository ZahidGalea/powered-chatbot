import core
from chatbot.pinecone_manager import PineconeClientManager


def load_google_docs_folder(documents_id, index_name_to_load):
    pinecone_manager = PineconeClientManager()
    get_indexes_and_vstore = pinecone_manager.get_indexes_and_vstore()
    for indexes_tuples in get_indexes_and_vstore.values():
        index_name, index, vector_store = indexes_tuples
        if index_name == index_name_to_load:
            storage_context, service_context, token_counter = core.build_pre_index(
                vector_store=vector_store,
                llm_type="openai",
            )

            pinecone_manager.load_google_doc_to_pinecone(
                index_name=index_name,
                service_context=service_context,
                storage_context=storage_context,
                documents_id=documents_id,
            )


if __name__ == "__main__":
    documents_id = ["1CxgqMrXRazO7tRbqwybP00MfCiGiCAPo3x7Eaq1VaMg"]

    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    SERVICE_ACCOUNT_FILE = '.json'

    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    load_google_docs_folder(documents_id, index_name_to_load="dataverse-docs")
