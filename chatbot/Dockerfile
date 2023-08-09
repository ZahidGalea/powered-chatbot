
ARG PYTHON_VERSION="3.9"

FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel
USER root
WORKDIR app

RUN apt update && apt install -y git
RUN pip install -U git+https://github.com/jerryjliu/llama_index.git
RUN pip install transformers==4.31.0 accelerate tiktoken einops
RUN pip install fastapi
RUN pip install pinecone-client
RUN pip install uvicorn
RUN pip install --upgrade typing_extensions
RUN pip install sentence_transformers~=2.2.2

COPY api.py .
COPY core.py .
COPY pinecone_manager.py .

ENTRYPOINT ["python","api.py"]