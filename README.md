##  Powered QA LLM


## Infrastructure

```bash
cd infrastructure/prod
export GOOGLE_APPLICATION_CREDENTIALS=.json
terraform plan -out=plan.tfplan
terraform apply "plan.tfplan"
```

```bash
terraform apply "plan.tfplan"
```

### Build the images first:

### Chatbot & UI

```bash
export VERSION=$(cat ./VERSION)
# Chatbot
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker build -t zahidgalea/powered-chatbot-app:latest ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
docker push zahidgalea/powered-chatbot-app:latest
# UI
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker build -t zahidgalea/chatbot-ui:latest ./ui
docker push zahidgalea/chatbot-ui:$VERSION
docker push zahidgalea/chatbot-ui:latest
```

## Deployment in K8S

In helm folder

```bash
export VERSION=$(cat ./VERSION)
cd helm
gcloud container clusters get-credentials chatbot-llm-gke --region us-east1 --project chatbot-llm-395402
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
kubectl config set-context --current --namespace=powered-chatbot
kubectl apply -f ./secrets/
```

```bash
kubectl config set-context --current --namespace=powered-chatbot
kubectl port-forward service/powered-chatbot-app-service 5001:5001 &
kubectl port-forward service/ui-service  80:80 &
```

### To develop UI

```bash
export VERSION=$(cat ./VERSION)
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker run -v ${pwd}/ui:/app/ zahidgalea/chatbot-ui:$VERSION
```

### Fast iteration deployment

```bash
export VERSION=$(cat ./VERSION)
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
cd helm
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
```


### To implement in future

https://gpt-index.readthedocs.io/en/latest/core_modules/query_modules/router/root.html