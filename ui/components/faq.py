# flake8: noqa
import streamlit as st


def faq():
    st.markdown(
        """
# FAQ
## How does this GPT work?
We have uploaded a bunch of excel files to a Document Database so
when you ask a question, This system will search through the
documents and find the most relevant ones using the vector index.
Then we use the result to generate an answer.


## Are the answers 100% accurate?
No, the answers are not 100% accurate. We are using open models,
Dont expect the performance of a gpt3 or gpt4 llm models.
If you need a 100% accurate answer get close to one of our leaders.
 @Naoto / @Zahid Galea 

## Limitations !Important

* The system just look for 5 chunks of information before giving the response
so the data could be limited
* We are using GPT3.5 Turbo
* The chat doesnt save any context, dont ask based on the last response.

## What are we using for this PoC?

* LlamaIndex and Langchain Framework
* Alibaba Qwen-7B as llm inference
* intfloat/e5-large-v2 as Embedding model
* Pinecone as VectorDB
* Streamlint and FastAPI for GUI and Backend.

"""
    )
