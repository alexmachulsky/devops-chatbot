# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the AI Chatbot.

## Architecture

- **Chatbot Application**: 2 replicas for high availability
- **Ollama Service**: Runs on host via Docker Compose (due to resource requirements)
- **Service Type**: NodePort for external access
- **Health Checks**: Liveness and readiness probes configured

## Prerequisites

- Kubernetes cluster (tested with Minikube v1.35.0)
- Docker for running Ollama
- kubectl configured
- At least 4GB free memory for chatbot pods
- Ollama running on host at port 11434

## Quick Start

### 1. Start Ollama (Docker Compose)

```bash
# Start Ollama service
docker-compose up -d ollama

# Pull the model
docker exec ollama-server ollama pull llama3.1:8b
```

### 2. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=devops-chatbot --timeout=60s

# Check status
kubectl get pods
```

### 3. Access the Application

#### Option A: Port Forwarding (Development)
```bash
kubectl port-forward svc/devops-chatbot 8888:80
```
Access at: http://localhost:8888

#### Option B: NodePort (Network Access)
```bash
# Get the NodePort
kubectl get svc devops-chatbot

# Access via Minikube IP
minikube service devops-chatbot --url
```

## Manifests Overview

### deployment.yaml
- **Replicas**: 2 pods for high availability
- **Image**: ai-chatbot:latest (built locally)
- **Resources**: 
  - Requests: 256Mi memory, 250m CPU
  - Limits: 512Mi memory, 500m CPU
- **Probes**: Liveness and readiness checks on `/api/health`
- **Environment**: Connects to Ollama at host IP (192.168.18.241:11434)

### service.yaml
- **Type**: NodePort
- **Port**: 80 (internal) → 5000 (container) → 30000 (external)
- **Session Affinity**: ClientIP (maintains user sessions)

### configmap.yaml
- **FLASK_ENV**: production
- **FLASK_DEBUG**: False
- **HOST**: 0.0.0.0
- **PORT**: 5000

### ollama-deployment.yaml
- **Note**: Optional K8s deployment for Ollama
- **Resource Requirements**: 4-12Gi memory (not recommended for Minikube)
- **Recommendation**: Use Docker Compose instead for better resource management

## Building and Deploying

### Build the Docker Image

For Minikube (uses Minikube's Docker daemon):
```bash
# Configure shell to use Minikube's Docker
eval $(minikube docker-env)

# Build the image
docker build -t ai-chatbot:latest .

# Verify
docker images | grep ai-chatbot
```

For other K8s clusters:
```bash
# Build and tag
docker build -t your-registry/ai-chatbot:latest .

# Push to registry
docker push your-registry/ai-chatbot:latest

# Update deployment.yaml with full image path
```

## Troubleshooting

### Pods not starting
```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod -l app=devops-chatbot

# Check logs
kubectl logs -l app=devops-chatbot
```

### Connection to Ollama fails
```bash
# Check Ollama is running
docker ps | grep ollama

# Test Ollama from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://192.168.18.241:11434/api/tags

# Update OLLAMA_URL in deployment.yaml if needed
```

### Out of resources
```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# Free up disk space
docker system prune -a
docker volume prune

# Increase Minikube resources
minikube stop
minikube start --memory=8192 --cpus=4
```

## Scaling

### Horizontal Scaling
```bash
# Scale up
kubectl scale deployment devops-chatbot --replicas=3

# Scale down
kubectl scale deployment devops-chatbot --replicas=1
```

### Auto-scaling (optional)
```bash
# Create HPA
kubectl autoscale deployment devops-chatbot \
  --cpu-percent=70 \
  --min=2 \
  --max=5
```

## Monitoring

### Check Health
```bash
# Via kubectl
kubectl exec -it deployment/devops-chatbot -- curl localhost:5000/api/health

# Via port-forward
curl http://localhost:8888/api/health
```

### View Logs
```bash
# All pods
kubectl logs -l app=devops-chatbot

# Specific pod
kubectl logs devops-chatbot-<pod-id>

# Follow logs
kubectl logs -l app=devops-chatbot -f

# Previous pod instance
kubectl logs -l app=devops-chatbot --previous
```

## Cleanup

```bash
# Delete deployment and service
kubectl delete -f k8s/

# Or delete by labels
kubectl delete deployment,service,configmap -l app=devops-chatbot

# Stop Ollama
docker-compose down

# Stop Minikube
minikube stop
```

## Production Considerations

For production deployment, consider:

1. **Security**:
   - Move SECRET_KEY to Kubernetes Secrets
   - Implement Network Policies
   - Add Pod Security Standards
   - Use RBAC for access control

2. **Ingress**:
   - Deploy Ingress Controller (nginx/traefik)
   - Configure TLS/HTTPS
   - Add authentication

3. **Monitoring**:
   - Deploy Prometheus + Grafana
   - Configure alerts
   - Log aggregation (ELK/Loki)

4. **High Availability**:
   - Multi-node cluster
   - Pod Disruption Budgets
   - Anti-affinity rules

5. **Ollama**:
   - Dedicated high-memory nodes
   - Persistent volumes for models
   - Consider managed AI services

## Architecture Decisions

### Why Ollama runs outside K8s?

The llama3.1:8b model requires 6-8GB of RAM to load and run effectively. In resource-constrained environments like Minikube:

- Running Ollama in K8s would consume most available memory
- Model loading can fail due to OOM (Out of Memory) errors
- Chatbot pods would be starved of resources

**Solution**: Run Ollama via Docker Compose on the host, allowing:
- Dedicated resources for model serving
- Stable performance without OOM kills
- K8s pods connect via host IP
- Better separation of concerns

For production with sufficient resources, use `ollama-deployment.yaml` to run Ollama inside K8s.

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Ollama Documentation](https://ollama.ai/docs/)
