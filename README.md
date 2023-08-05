###    

## Build the images first:

### Chatbot & UI

```bash
export VERSION=$(cat ./VERSION)
# Chatbot
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
# UI
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker push zahidgalea/chatbot-ui:$VERSION
```

### ChromaDB

```bash
docker build -t zahidgalea/chromadb:latest ./chroma
docker push zahidgalea/chromadb:latest
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
export VERSION=$(cat ./VERSION)
cd helm
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
```

To access the embedding and database Api

```bash
kubectl config set-context --current --namespace=powered-chatbot
kubectl port-forward service/chromadb-service 8000:8000 &
```

### To develop UI

```bash
export VERSION=$(cat ./VERSION)
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker run -v ${pwd}/ui:/app/ zahidgalea/chatbot-ui:$VERSION
```