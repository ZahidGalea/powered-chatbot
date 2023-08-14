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
from llama_index.embeddings.openai import OpenAIEmbeddingMode, OpenAIEmbeddingModelType
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.node_parser import SentenceWindowNodeParser, SimpleNodeParser
from llama_index.node_parser.extractors import (
    KeywordExtractor,
    MetadataExtractor,
)
from llama_index.text_splitter import SentenceSplitter

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def get_openai_embedding_model():
    return OpenAIEmbedding(
        model=OpenAIEmbeddingModelType.TEXT_EMBED_ADA_002,
        mode=OpenAIEmbeddingMode.TEXT_SEARCH_MODE,
    )


def get_e5_large_embedding_model():
    from sentence_transformers import SentenceTransformer

    class e5Model(BaseEmbedding):
        def __init__(
            self,
            model_name: str = "intfloat/multilingual-e5-large",
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
    )


def get_sentence_node_parser():
    logging.info("Getting default sentence node parser")
    return SentenceWindowNodeParser.from_defaults(
        include_metadata=True,
        window_size=9,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
        sentence_splitter=SentenceSplitter(
            separator="\n", chunk_overlap=5, chunk_size=60
        ).split_text,
        metadata_extractor=MetadataExtractor(
            extractors=[
                KeywordExtractor(keywords=5),
            ],
        ),
    )


def get_openai_llm(
    model_name,
    model_temperature=0.7,
):
    logging.info("Getting OpenAI LLM")
    return OpenAIChat(
        model_name=model_name,
        prefix_messages=[
            {
                "role": "system",
                "content": """
You will be provided with information that comes from documents nodes, the metadata will be available,
 try to join them, and your task is to answer the user question, following these rules:

- You dont have any previous knowledge, everything comes from the document nodes
- If you dont know the answer just say it, and reference Naoto or Zahid for help
- If applicable, a list of examples that exists in the document
- You are a system part of Acid Labs companies, and all the users are from Acid labs too
""",
            },
            {
                "role": "user",
                "content": "I'm a worker at Acid Labs, a technology consulting company. "
                "I want to know more about the context that I will define that comes from documents of my company.",
            },
            {
                "role": "assistant",
                "content": "I am an assistant that is friendly and a little bit funny, also I like to add slack emojis",
            },
        ],
        temperature=model_temperature,
    )


def get_prompt_helper():
    logging.info("Getting default promp helper")
    return PromptHelper(
        context_window=DEFAULT_CONTEXT_WINDOW,
        num_output=DEFAULT_NUM_OUTPUTS,
        chunk_overlap_ratio=0.2,
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
            llm = get_openai_llm("gpt-3.5-turbo")
        else:
            raise Exception(f"llm not in expected: {llm_type}")

    token_counter = TokenCountingHandler(
        tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
    )

    callback_manager = CallbackManager([token_counter])
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model or get_openai_embedding_model(),
        llm=llm,
        prompt_helper=prompt_helper or get_prompt_helper(),
        node_parser=node_parser or get_sentence_node_parser(),
        callback_manager=callback_manager,
    )
    return storage_context, service_context, token_counter
