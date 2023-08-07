import logging
import os

import openai
import uvicorn
from fastapi import FastAPI, Request
from llama_index import Prompt, VectorStoreIndex
from llama_index.prompts.prompt_type import PromptType

import core
from pinecone_manager import PineconeClientManager

app = FastAPI()

openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.post("/query")
async def query(request: Request):
    data = await request.json()
    text = data.get("text")
    required_index_name = data.get("required_index_name")

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

    vector_store_index: VectorStoreIndex = vector_store_indexes[required_index_name]

    query_engine = vector_store_index.as_query_engine(
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

    pinecone_manager = PineconeClientManager()
    
    get_indexes_and_vstore = pinecone_manager.get_indexes_and_vstore()
    vector_store_indexes = {}
    for indexes_tuples in get_indexes_and_vstore.values():
        index_name, index, vector_store = indexes_tuples
        _, service_context = core.build_pre_index(
            vector_store=vector_store,
            llm_type="openai",
        )
        vector_store_indexes[index_name] = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, service_context=service_context
        )

    uvicorn.run(app, host="0.0.0.0", port=5001)
