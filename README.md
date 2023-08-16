# Powered QA LLM

## Table of Contents
- [Infrastructure Setup](#infrastructure-setup)
- [Building Docker Images](#building-docker-images)
  - [Chatbot & UI](#chatbot--ui)
- [Deployment in Kubernetes (K8S)](#deployment-in-kubernetes-k8s)
- [Development and Iteration](#development-and-iteration)
  - [UI Development](#ui-development)
  - [Fast Iteration Deployment](#fast-iteration-deployment)
- [Future Implementation](#future-implementation)
- [Collaboration Rules](#collaboration-rules)

## Infrastructure Setup

Navigate to the production infrastructure directory:
```bash
cd infrastructure/prod
export GOOGLE_APPLICATION_CREDENTIALS=.json
terraform plan -out=plan.tfplan
terraform apply "plan.tfplan"
```

## Building Docker Images

### Chatbot & UI
Set the version:
```bash
export VERSION=$(cat ./VERSION)
```
#### Chatbot core
```bash
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker build -t zahidgalea/powered-chatbot-app:latest ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
docker push zahidgalea/powered-chatbot-app:latest
```
#### Chatbot UI
```bash
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker build -t zahidgalea/chatbot-ui:latest ./ui
docker push zahidgalea/chatbot-ui:$VERSION
docker push zahidgalea/chatbot-ui:latest
```

## Deployment in Kubernetes (K8S)

Navigate to the helm folder and set up the app cluster:
```bash
export VERSION=$(cat ./VERSION)
cd helm
gcloud container clusters get-credentials chatbot-llm-gke --region us-east1 --project chatbot-llm-395402
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
kubectl config set-context --current --namespace=powered-chatbot
kubectl apply -f ./secrets/
```
To forward from kubernetes to localhost
```bash
kubectl port-forward service/powered-chatbot-app-service 5001:5001 &
kubectl port-forward service/ui-service  80:80 &
```

## Development and Iteration

### UI Development
```bash
export VERSION=$(cat ./VERSION)
docker build -t zahidgalea/chatbot-ui:$VERSION ./ui
docker run -v ${pwd}/ui:/app/ zahidgalea/chatbot-ui:$VERSION
```
### Bot Development



### Fast Iteration Deployment

Build, push, and deploy changes quickly:
```bash
export VERSION=$(cat ./VERSION)
docker build -t zahidgalea/powered-chatbot-app:$VERSION ./chatbot
docker push zahidgalea/powered-chatbot-app:$VERSION
cd helm
helm upgrade powered-chatbot . --namespace powered-chatbot --install --create-namespace --debug --set app_version=$VERSION
```

## Future Implementation
[View the future implementations here.](https://gpt-index.readthedocs.io/en/latest/core_modules/query_modules/router/root.html)

## Collaboration Rules
1. **Branching**: Always create a feature branch for any new feature or fix. Do not push directly to the `main` branch.
2. **Commit Messages**: Ensure your commit messages are meaningful and follow best practices.
3. **Code Reviews**: Every pull request should be reviewed by at least one other developer before merging into the `main` branch.
4. **Testing**: Ensure that all unit tests pass before submitting a pull request. Add new tests for new features.
5. **Documentation**: Update the documentation as needed when adding or modifying features.