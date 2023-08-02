
ARG PYTHON_VERSION="3.9"

FROM python:${PYTHON_VERSION}
USER root
WORKDIR app

RUN pip install chromadb-client
RUN pip install pdfplumber=="0.10.2"
RUN pip install flask flask-requests
RUN pip install fastapi
RUN pip install uvicorn
RUN pip install httpx
RUN pip install streamlit

COPY . .

ENTRYPOINT ["streamlit","run","/app/ui.py"]
