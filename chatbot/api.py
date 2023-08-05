import logging
import os

import openai
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from llama_index import Prompt, PromptHelper
from llama_index.constants import DEFAULT_CONTEXT_WINDOW, DEFAULT_NUM_OUTPUTS
from llama_index.prompts.prompt_type import PromptType
from llama_index.query_engine import RetrieverQueryEngine

import core
from chroma_client import ChromaDBClient, ChromaDBCollections

app = FastAPI()

load_dotenv(override=True)
openai.api_key = os.environ.get("OPENAI_API_KEY")
CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "host.docker.internal")
CHROMADB_PORT = os.environ.get("CHROMADB_PORT", "8000")


def create_index(chroma_collection_name, service_context, vector_store):
    index = core.get_index(
        _chroma_collection_name=chroma_collection_name,
        vector_store=vector_store,
        service_context=service_context,
    )
    return index


@app.get("/files_loaded")
async def files_loaded():
    data: list = chromadb_client.list_files_loaded_per_collection()
    return {"files_loaded": data}


@app.post("/query")
async def query(request: Request):
    data = await request.json()
    text = data.get("text")

    if text is None:
        return "No text field provided"

    logging.info(f"Question required: {text}")
    # Must begin with user
    default_text_qa_prompt_tmpl = (
        "user:\n"
        "Consider this information:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Answer the question: {query_str}\n"
    )
    default_text_qa_prompt = Prompt(
        default_text_qa_prompt_tmpl, prompt_type=PromptType.QUESTION_ANSWER
    )

    query_engine: RetrieverQueryEngine = index.as_query_engine(
        similarity_top_k=5,
        verbose=True,
        text_qa_template=default_text_qa_prompt,
        response_mode="simple_summarize",
    )

    response = query_engine.query(text)

    return {
        "response": response.response,
        "nodes": [
            (node.node.metadata["file_name"], node.node.get_content())
            for node in response.source_nodes
        ],
    }


if __name__ == "__main__":
    logging.info("Iniciando la aplicación FastAPI...")

    embedding_model = core.get_embedding_model()
    chromadb_client = ChromaDBClient(
        host=CHROMADB_HOST,
        port=CHROMADB_PORT,
    )
    llm = core.get_llm(model_temperature=0.5)

    prompt_helper = PromptHelper(
        context_window=DEFAULT_CONTEXT_WINDOW,
        num_output=DEFAULT_NUM_OUTPUTS,
        chunk_overlap_ratio=0.1,
        chunk_size_limit=None,
    )
    node_parser = core.get_node_parser()

    storage_context, service_context, vector_store = core.build_pre_index(
        _chroma_collection_name=ChromaDBCollections.default_collection,
        remote_db=chromadb_client.client,
        node_parser=node_parser,
        llm=llm,
        embed_model=embedding_model,
        prompt_helper=prompt_helper,
    )
    index = create_index(
        ChromaDBCollections.default_collection,
        service_context=service_context,
        vector_store=vector_store,
    )
    uvicorn.run(app, host="0.0.0.0", port=5001)
