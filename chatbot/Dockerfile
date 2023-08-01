
ARG PYTHON_VERSION="3.9"

FROM python:${PYTHON_VERSION}
USER root
WORKDIR app

RUN pip install -U git+https://github.com/jerryjliu/llama_index.git
RUN pip install pypdf
RUN pip install chromadb-client
RUN pip install sentence-transformers
RUN pip install pydantic==1.10.11
RUN pip install tiktoken
RUN pip install gpt4all
RUN pip install einops
RUN pip install pdfplumber=="0.10.2"
RUN pip install flask flask-requests
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install httpx
RUN pip install python-dotenv

COPY api.py .
COPY common.py .
COPY chromadb_client.py .

ENTRYPOINT ["python","api.py"]