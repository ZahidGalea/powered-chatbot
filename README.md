###    

## Build the images first:

### Chatbot

```bash
export VERSION=$(cat ./app/VERSION)
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
```

### ChromaDB

```bash
docker build -t zahidgalea/chromadb:latest ./chroma
docker push zahidgalea/chromadb:latest
```

### Streamlit UI

```bash
docker build -t zahidgalea/chatbot-ui:latest ./ui
docker push zahidgalea/chatbot-ui:latest
```

## Deployment in K8S

In helm folder

```bash
cd helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm search repo bitnami
helm dependency update
helm dependency build
kubectl config set-context --current --namespace=powered-chatbot
```

```bash
cd helm
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug
```

To access the embedding and database Api

```bash
kubectl config set-context --current --namespace=powered-chatbot
kubectl port-forward service/chromadb-service 8000:8000 &
```

### To develop UI

```bash
docker run -v /C:/Users/zahid/PycharmProjects/powered-chatbot/ui/:/app/ ui:latest
```