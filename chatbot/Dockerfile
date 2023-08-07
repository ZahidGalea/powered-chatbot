
ARG PYTHON_VERSION="3.9"

FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel
USER root
WORKDIR app

RUN apt update && apt install -y git
RUN pip install -U git+https://github.com/jerryjliu/llama_index.git
RUN pip install transformers==4.31.0 accelerate tiktoken einops
RUN pip install fastapi
RUN pip install pinecone-client
RUN git clone -b v1.0.8 https://github.com/Dao-AILab/flash-attention
RUN cd flash-attention && pip install .
RUN cd flash-attention && pip install csrc/layer_norm
RUN cd flash-attention && pip install csrc/rotary
RUN pip install uvicorn
RUN pip install --upgrade typing_extensions
RUN pip install sentence_transformers~=2.2.2
# Llamaindex required to load pdf
RUN pip install pypdf


COPY api.py .
COPY core.py .
COPY pinecone_manager.py .

ENTRYPOINT ["python","api.py"]