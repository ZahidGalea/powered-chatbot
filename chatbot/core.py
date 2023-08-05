import logging
import sys

from langchain.llms import OpenAIChat
from llama_index import (
    OpenAIEmbedding,
    ServiceContext,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.constants import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.node_parser import SimpleNodeParser
from llama_index.prompts import Prompt
from llama_index.vector_stores import ChromaVectorStore

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def get_embedding_model():
    return OpenAIEmbedding(embed_batch_size=42)


def get_default_prompts():
    text_qa_template_str = (
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Using both the context information and also using your own knowledge, "
        "Answer the question: {query_str}\n"
        "If the context isn't helpful, Just result 'I Dont know what to say'.\n"
    )
    text_qa_template = Prompt(text_qa_template_str)

    refine_template_str = (
        "The original question is as follows: {query_str}\n"
        "We have provided an existing answer: {existing_answer}\n"
        "We have the opportunity to refine the existing answer "
        "(only if needed) with some more context below.\n"
        "------------\n"
        "{context_msg}\n"
        "------------\n"
        "Using both the new context and your own knowledege, update or repeat the existing answer.\n"
    )

    refine_template = Prompt(refine_template_str)

    system_prompts_str = """
# Chatbot Model
- Chatbot Model is a helpful and harmless open-source AI language model developed by Someone.
- Chatbot Model is more than just an information source, Chatbot Model is also able to write poetry, short stories, and make jokes.
"""

    return text_qa_template, refine_template, system_prompts_str


def get_node_parser(chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP):
    return SimpleNodeParser(
        text_splitter=TokenTextSplitter(
            separator=" ",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            backup_separators=["\n"],
        ),
        include_metadata=True,
        metadata_extractor=None,
    )


def get_index(_chroma_collection_name, service_context, vector_store):
    _index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store, service_context=service_context
    )
    return _index


def get_llm(
    model_temperature=0.7,
):
    return OpenAIChat(
        model_name="gpt-3.5-turbo",
        prefix_messages=[
            {
                "role": "assistant",
                "content": "You are an AI assistant of the company Acid Labs. You use a tone that is friendly, technical and scientific.",
            },
            {
                "role": "user",
                "content": "Im a worker at Acid Labs that wants to know more about my company",
            },
            {
                "role": "assistant",
                "content": "You are an AI assistant that gives answer about documentation in a context only in english language",
            },
        ],
        temperature=model_temperature,
    )


def build_pre_index(
    _chroma_collection_name,
    remote_db,
    embed_model,
    node_parser,
    llm=None,
    prompt_helper=None,
):
    chroma_collection = remote_db.get_or_create_collection(_chroma_collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        llm=llm,
        prompt_helper=prompt_helper,
        node_parser=node_parser,
    )
    return storage_context, service_context, vector_store
