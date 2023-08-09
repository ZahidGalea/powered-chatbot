##  Powered QA LLM


## Infrastructure

```bash
cd infrastructure/prod
export GOOGLE_APPLICATION_CREDENTIALS=.json
terraform plan -out=plan.tf
```

```bash
terraform apply "plan.tf"
```

### Build the images first:

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

## Deployment in K8S

In helm folder

```bash
kubectl config set-context --current --namespace=powered-chatbot
export VERSION=$(cat ./VERSION)
cd helm
kubectl apply -f ./secrets/
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
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