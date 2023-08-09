import logging
import sys
from typing import Any, List

import tiktoken
from langchain.llms import OpenAIChat
from llama_index import (
    OpenAIEmbedding,
    PromptHelper,
    ServiceContext,
    StorageContext,
)
from llama_index.callbacks import CallbackManager, TokenCountingHandler
from llama_index.constants import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONTEXT_WINDOW,
    DEFAULT_NUM_OUTPUTS,
)
from llama_index.embeddings.base import BaseEmbedding
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.node_parser import SimpleNodeParser
from llama_index.prompts import Prompt

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def get_openai_embedding_model():
    return OpenAIEmbedding(embed_batch_size=42)


def get_e5_large_embedding_model():
    from sentence_transformers import SentenceTransformer

    class e5Model(BaseEmbedding):
        def __init__(
            self,
            model_name: str = "intfloat/e5-large-v2",
            **kwargs: Any,
        ) -> None:
            self._model = SentenceTransformer(model_name, cache_folder="./")
            super().__init__(**kwargs)

        def _get_query_embedding(self, query: str) -> List[float]:
            embeddings = self._model.encode(
                sentences=f"query: {query}",
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return embeddings.tolist()

        def _get_text_embedding(self, text: str) -> List[float]:
            embeddings = self._model.encode(
                sentences=f"passage: {text}",
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return embeddings.tolist()

        def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
            embeddings = self._model.encode(
                sentences=[f"passage: {text}" for text in texts],
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return embeddings.tolist()

    model = e5Model()
    return model


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
    logging.info("Getting default get node parser")
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


def get_openai_llm(
    model_temperature=0.7,
):
    logging.info("Getting OpenAI LLM")
    return OpenAIChat(
        model_name="gpt-3.5-turbo",
        prefix_messages=[
            {
                "role": "assistant",
                "content": "You are an Assistant of the company Acid Labs. You use a tone that is friendly, and funny.",
            },
            {
                "role": "user",
                "content": "Im a worker at Acid Labs, that wants to know more about my company",
            },
            {
                "role": "assistant",
                "content": "You are an Assistant that gives answer about documentation in the context",
            },
        ],
        temperature=model_temperature,
    )


def get_prompt_helper():
    logging.info("Getting default promp helper")
    return PromptHelper(
        context_window=DEFAULT_CONTEXT_WINDOW,
        num_output=DEFAULT_NUM_OUTPUTS,
        chunk_overlap_ratio=0.1,
        chunk_size_limit=None,
    )


def build_pre_index(
    vector_store,
    llm_type: str = "openai",
    embed_model=None,
    node_parser=None,
    prompt_helper=None,
):
    llm = None
    if llm_type:
        if llm_type == "openai":
            llm = get_openai_llm()
        else:
            raise Exception(f"llm not in expected: {llm_type}")

    token_counter = TokenCountingHandler(
        tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
    )

    callback_manager = CallbackManager([token_counter])
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model or get_e5_large_embedding_model(),
        llm=llm,
        prompt_helper=prompt_helper or get_prompt_helper(),
        node_parser=node_parser or get_node_parser(),
        callback_manager=callback_manager,
    )
    return storage_context, service_context, token_counter
