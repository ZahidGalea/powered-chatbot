import logging
import os

import requests
import uvicorn
from fastapi import FastAPI, Request
from langchain.llms import openai
from llama_index import Prompt, VectorStoreIndex
from llama_index.prompts.prompt_type import PromptType
from starlette.background import BackgroundTasks

import core
from pinecone_manager import PineconeClientManager

app = FastAPI()

assert os.environ.get("OPENAI_API_KEY")
openai.api_key = os.environ.get("OPENAI_API_KEY")
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")


@app.post("/slack/dataverse")
async def slack_dataverse(request: Request, background_tasks: BackgroundTasks):
    async def process_query(prompt, query_text, top_k, _index, url_to_response):
        vector_store_index: VectorStoreIndex = vector_store_indexes[_index]

        query_engine = vector_store_index.as_query_engine(
            similarity_top_k=top_k,
            verbose=True,
            text_qa_template=prompt,
            response_mode="simple_summarize",
        )

        response = query_engine.query(query_text)

        payload = {
            "response_type": "in_channel",
            "replace_original": True,
            "text": f"---- {query_text} ----\n{response.response}",
        }
        requests.post(url_to_response, json=payload)

    form_data = await request.form()
    logging.debug(form_data)

    text = form_data.get("text")
    channel_name = form_data.get("channel_name")
    user_name = form_data.get("user_name")
    response_url = form_data.get("response_url")

    if channel_name != "dataverse-question-aswering":
        return {
            "text": "You cant use this channel, you have to move to dataverse-secretary channel",
        }

    if text is None:
        return "No text field provided"

    logging.info(f"Question required: {text}")
    default_text_qa_prompt_tmpl = (
        f"user: I am {user_name}, a worker at Acidlabs"
        "Consider the following context:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Based on the context and nothing else, "
        "Answer this question (Translate the answer to the language of the question!): {query_str}\n"
        'If you dont know it, please just say: "I dont have enough documentation for this question, '
        'get close to Naoto or Zahid"'
    )
    default_text_qa_prompt = Prompt(
        default_text_qa_prompt_tmpl, prompt_type=PromptType.QUESTION_ANSWER
    )

    background_tasks.add_task(
        process_query,
        default_text_qa_prompt,
        text,
        6,
        "dataverse-chatbot",
        response_url,
    )

    return {
        "text": "Wait a little bit... processing response",
    }


@app.post("/query/dataverse")
async def query_dataverse(request: Request):
    data = await request.json()
    text = data.get("text")

    if text is None:
        return "No text field provided"

    logging.info(f"Question required: {text}")
    # Must begin with user
    default_text_qa_prompt_tmpl = (
        f"user: I am zahid.galea, a worker at Acidlabs"
        "Consider the following context:\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Based on the context and nothing else, "
        "Answer this question (Translate the answer to the language of the question!): {query_str}\n"
        'If you dont know it, please just say: "I dont have enough documentation for this question, '
        'get close to Naoto or Zahid"'
    )
    default_text_qa_prompt = Prompt(
        default_text_qa_prompt_tmpl, prompt_type=PromptType.QUESTION_ANSWER
    )

    vector_store_index: VectorStoreIndex = vector_store_indexes["dataverse-chatbot"]

    query_engine = vector_store_index.as_query_engine(
        similarity_top_k=5,
        verbose=True,
        text_qa_template=default_text_qa_prompt,
        response_mode="simple_summarize",
    )

    response = query_engine.query(text)

    total_llm_tokens = token_counter.total_llm_token_count

    token_counter.reset_counts()

    return {
        "response": response.response,
        "nodes": [
            (node.node.metadata["file_name"], node.node.get_content())
            for node in response.source_nodes
        ],
        "tokens": {"total_llm": total_llm_tokens},
    }


if __name__ == "__main__":
    logging.info("Iniciando la aplicación FastAPI...")

    pinecone_manager = PineconeClientManager()

    get_indexes_and_vstore = pinecone_manager.get_indexes_and_vstore()
    vector_store_indexes = {}
    for indexes_tuples in get_indexes_and_vstore.values():
        index_name, index, vector_store = indexes_tuples
        _, service_context, token_counter = core.build_pre_index(
            vector_store=vector_store,
            llm_type="openai",
        )
        vector_store_indexes[index_name] = VectorStoreIndex.from_vector_store(
            vector_store=vector_store, service_context=service_context
        )

    uvicorn.run(app, host="0.0.0.0", port=5001)
