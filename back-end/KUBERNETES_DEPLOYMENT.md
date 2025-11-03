# Kubernetes Deployment Guide

This guide explains how to deploy the ParagonAI back-end to Kubernetes using the provided manifest.

## Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured to access your cluster
- Docker image built and pushed to a registry
- API keys for LLM services (GROQ, OpenAI, etc.)

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build the Docker image
cd back-end
docker build -t your-registry/paragonai-backend:latest .

# Push to your registry
docker push your-registry/paragonai-backend:latest
```

### 2. Update the Manifest

Edit [kubernetes-manifest.yaml](kubernetes-manifest.yaml) and update:

- Line 157: Replace `hmbaytam/paragonai-backend:latest` with your actual image (or keep it if using this image)

**Note**: If you don't have a domain or aren't using Ingress yet, you can skip the Ingress configuration. The application will still be accessible via other methods (see "Access Without Ingress" section below).

### 3. Create Secrets

Create a secrets file with your actual values:

```bash
# Create a temporary file with your secrets
cat > secrets.env <<EOF
GROQ_API_KEY=your-groq-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-password
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
EOF

# Create the secret in Kubernetes
kubectl create secret generic backend-secrets \
  --from-env-file=secrets.env \
  --namespace=paragonai \
  --dry-run=client -o yaml | kubectl apply -f -

# Remove the temporary file
rm secrets.env
```

Alternatively, manually encode values and update the Secret in the manifest:

```bash
echo -n 'your-groq-api-key' | base64
```

### 4. Deploy to Kubernetes

```bash
# Apply the manifest
kubectl apply -f kubernetes-manifest.yaml

# Verify the deployment
kubectl get all -n paragonai

# Check pod status
kubectl get pods -n paragonai -w
```

### 5. Access the Application

## Access Without Ingress

If you don't have a domain or Ingress controller, here are three ways to access your application:

### Option 1: Port Forward (Development/Testing)
Best for local development and testing:

```bash
# Forward the backend service to your local machine
kubectl port-forward -n paragonai svc/backend 8000:8000

# Access the API at http://localhost:8000
# Access the docs at http://localhost:8000/docs
# In another terminal, forward metrics port
kubectl port-forward -n paragonai svc/backend 8001:8001
```

**Pros**: Simple, secure, no external exposure
**Cons**: Only works from your machine, connection dies if terminal closes

### Option 2: NodePort Service (Quick External Access)
Exposes the service on each node's IP at a static port:

```bash
# Modify the backend service to use NodePort
kubectl patch service backend -n paragonai -p '{"spec":{"type":"NodePort"}}'

# Get the NodePort assigned
kubectl get svc backend -n paragonai

# Access via: http://<NODE_IP>:<NODE_PORT>
# Get node IPs with:
kubectl get nodes -o wide
```

Example output:
```
NAME      TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
backend   NodePort   10.96.123.45    <none>        8000:30123/TCP,8001:30124/TCP   5m
```

Access at: `http://<any-node-ip>:30123`

**Pros**: External access without Ingress
**Cons**: Exposes high port numbers (30000-32767), not ideal for production

### Option 3: LoadBalancer Service (Cloud Provider)
If running on a cloud provider (AWS, GCP, Azure):

```bash
# Change service type to LoadBalancer
kubectl patch service backend -n paragonai -p '{"spec":{"type":"LoadBalancer"}}'

# Wait for external IP to be assigned (may take 1-2 minutes)
kubectl get svc backend -n paragonai -w

# Once EXTERNAL-IP shows, access via:
# http://<EXTERNAL-IP>:8000
```

Example output:
```
NAME      TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)                         AGE
backend   LoadBalancer   10.96.123.45    203.0.113.42      8000:30123/TCP,8001:30124/TCP   5m
```

Access at: `http://203.0.113.42:8000`

**Pros**: Production-ready, cloud-native, gets real external IP
**Cons**: Costs money, requires cloud provider

### Option 4: Using Ingress (Future/Production)
When you're ready for production with a domain:

1. Install an Ingress controller:
```bash
# For nginx-ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```

2. Update the Ingress resource in the manifest with your domain
3. Point your domain's DNS to the Ingress controller's external IP

## Recommended Approach by Use Case

- **Local development**: Use **Port Forward** (Option 1)
- **Team testing**: Use **NodePort** (Option 2) or **Port Forward**
- **Cloud deployment**: Use **LoadBalancer** (Option 3)
- **Production with domain**: Use **Ingress** (Option 4)

## Manifest Components

### Namespace
- Creates a dedicated `paragonai` namespace for isolation

### ConfigMap (`backend-config`)
- Non-sensitive configuration values
- API settings, LLM defaults, MongoDB connection, etc.

### Secret (`backend-secrets`)
- Sensitive data (API keys, passwords)
- Must be base64-encoded
- Optional values marked with `optional: true`

### MongoDB
- **Deployment**: Single replica MongoDB instance
- **Service**: ClusterIP service on port 27017
- **PVC**: 10Gi persistent volume for data storage

### Backend Application
- **Deployment**:
  - 3 replicas for high availability
  - Rolling update strategy
  - Health checks (liveness & readiness probes)
  - Resource limits: 512Mi memory, 500m CPU
  - Resource requests: 256Mi memory, 250m CPU

- **Service**: ClusterIP exposing ports:
  - 8000: Main API
  - 8001: Prometheus metrics

- **Ingress**: Optional external access via domain

### HorizontalPodAutoscaler
- Auto-scales between 3-10 replicas
- Based on CPU (70%) and memory (80%) utilization

## Monitoring

The application exposes Prometheus metrics on port 8001:

```bash
# Check metrics
kubectl port-forward -n paragonai svc/backend 8001:8001
curl http://localhost:8001/metrics
```

Annotations are configured for Prometheus scraping:
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8001"
prometheus.io/path: "/metrics"
```

## Health Checks

The deployment includes health probes:

- **Liveness Probe**: `/api/v1/health` on port 8000
  - Initial delay: 30s
  - Period: 10s

- **Readiness Probe**: `/api/v1/health` on port 8000
  - Initial delay: 10s
  - Period: 5s

Make sure your application implements this health endpoint.

## Scaling

### Manual Scaling
```bash
# Scale to 5 replicas
kubectl scale deployment backend -n paragonai --replicas=5
```

### Auto-scaling
The HorizontalPodAutoscaler is configured to scale automatically based on resource usage.

## Troubleshooting

### Check pod logs
```bash
kubectl logs -n paragonai -l app=backend --tail=100 -f
```

### Check pod events
```bash
kubectl describe pod -n paragonai <pod-name>
```

### Check service endpoints
```bash
kubectl get endpoints -n paragonai backend
```

### Verify ConfigMap and Secrets
```bash
kubectl get configmap backend-config -n paragonai -o yaml
kubectl get secret backend-secrets -n paragonai -o yaml
```

### Common Issues

1. **ImagePullBackOff**: Update the image name in the Deployment spec
2. **CrashLoopBackOff**: Check logs and ensure all required secrets are set
3. **MongoDB connection failed**: Verify MongoDB pod is running
4. **Missing API keys**: Ensure secrets are properly base64-encoded

## Updating the Deployment

```bash
# After making changes to the manifest
kubectl apply -f kubernetes-manifest.yaml

# Watch rollout status
kubectl rollout status deployment/backend -n paragonai

# Rollback if needed
kubectl rollout undo deployment/backend -n paragonai
```

## Clean Up

```bash
# Delete all resources
kubectl delete namespace paragonai
```

## Production Considerations

1. **Persistent Storage**: Consider using a cloud provider's storage class for MongoDB PVC
2. **Database**: Use managed MongoDB service (Atlas, DocumentDB) instead of in-cluster MongoDB
3. **Secrets Management**: Use external secrets managers (AWS Secrets Manager, HashiCorp Vault)
4. **TLS/HTTPS**: Configure TLS certificates for the Ingress
5. **Network Policies**: Add NetworkPolicy resources for security
6. **Resource Limits**: Adjust based on actual usage patterns
7. **Backup**: Implement MongoDB backup strategy
8. **Monitoring**: Deploy Prometheus and Grafana for full observability
9. **Image Registry**: Use private registry with imagePullSecrets
10. **Multi-region**: Consider multi-cluster deployment for HA

## Environment-Specific Configurations

Create separate manifests or use tools like Kustomize/Helm for:
- Development
- Staging
- Production

Example with Kustomize overlays:
```
k8s/
├── base/
│   └── kubernetes-manifest.yaml
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── prod/
```
