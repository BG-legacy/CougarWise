# Kubernetes Configuration for CougarWise Backend

This directory contains Kubernetes configuration files for deploying the CougarWise backend application with proper load balancing and data flow management.

## Components

- **deployment.yaml**: Defines the backend deployment with 3 replicas for high availability
- **service.yaml**: Creates a ClusterIP service to expose the backend within the cluster
- **ingress.yaml**: Sets up an Nginx Ingress controller for load balancing and routing
- **configmap.yaml**: Stores environment variables for the backend application
- **mongodb.yaml**: 
- **hpa.yaml**: Horizontal Pod Autoscaler for dynamically scaling based on load
- **kustomization.yaml**: Kustomize configuration to manage all resources

## Key Features

1. **Load Balancing**: The Nginx Ingress controller distributes traffic evenly across backend pods
2. **High Availability**: Multiple replicas ensure service continuity if a pod fails
3. **Autoscaling**: HPA automatically scales pods based on CPU and memory utilization
4. **Data Flow Management**: Proper service discovery and networking between components
5. **Persistent Storage**: PostgreSQL data persists across pod restarts

## Deployment Instructions

1. Make sure you have kubectl and a Kubernetes cluster set up
2. Deploy the Nginx Ingress Controller if not already installed:
   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
   ```

3. Deploy all resources using Kustomize:
   ```bash
   kubectl apply -k .
   ```

4. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get svc
   kubectl get ingress
   ```

5. Access the API through the Ingress controller's external IP.

## Configuration

Update the `configmap.yaml` file with your specific environment variables before deployment, especially:
- `OPENAI_API_KEY`
- `SECRET_KEY`
- Database credentials if different from defaults 

## Testing the Kubernetes Deployment

To test the deployment locally before applying it to a production cluster, follow these steps:

### Prerequisites
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) - For local Kubernetes testing
- [kubectl](https://kubernetes.io/docs/tasks/tools/) - Kubernetes command-line tool
- [Docker](https://docs.docker.com/get-docker/) - For building the container image

### Step 1: Start Minikube
```bash
# Start minikube with enough resources
minikube start --cpus=4 --memory=8192
```

### Step 2: Build and Load the Docker Image
```bash
# Navigate to the backend directory
cd backend

# Build the Docker image
docker build -t cougarwise-backend:latest .

# Load the image into Minikube
minikube image load cougarwise-backend:latest
```

### Step 3: Deploy the Application
```bash
# Navigate to the k8s directory
cd k8s

# Apply all resources using Kustomize
kubectl apply -k .
```

### Step 4: Verify the Deployment
```bash
# Check if pods are running
kubectl get pods

# Check MongoDB deployment
kubectl get deployment mongodb

# Check backend deployment
kubectl get deployment cougarwise-backend

# Check services
kubectl get svc

# Check ingress
kubectl get ingress
```

### Step 5: Test API Access
```bash
# Enable port-forwarding to access the service
kubectl port-forward svc/cougarwise-backend-service 8000:8000
```

Then open a browser or use curl to test the API:
```bash
curl http://localhost:8000/api/health
```

### Step 6: Test MongoDB Connection
```bash
# Get the name of the MongoDB pod
MONGO_POD=$(kubectl get pods -l app=mongodb -o jsonpath='{.items[0].metadata.name}')

# Connect to MongoDB to verify it's working
kubectl exec -it $MONGO_POD -- mongo
```

Inside the MongoDB shell, you can verify the database:
```javascript
use cougarwise
db.getCollectionNames()
```

### Step 7: Clean Up After Testing
```bash
# Delete all resources
kubectl delete -k .

# Stop minikube if no longer needed
minikube stop
```

## Automated Testing

For convenience, a test script has been provided to automate the testing process:

```bash
# Make sure the script is executable
chmod +x test-script.sh

# Run the test script
./test-script.sh
```

The script will:
1. Check for required tools (kubectl, minikube, docker)
2. Start minikube if it's not running
3. Build and load the Docker image
4. Deploy all Kubernetes resources
5. Wait for deployments to be ready
6. Check the status of all resources
7. Test API access with port forwarding
8. Test MongoDB connection
9. Provide a summary and cleanup options

## Monitoring with Kubernetes Dashboard

You can also deploy the Kubernetes Dashboard for visual monitoring:

```bash
# Deploy the standard Kubernetes Dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml

# Apply dashboard access configuration
kubectl apply -f test-dashboard.yaml

# Create a token for dashboard access
kubectl -n kubernetes-dashboard create token admin-user

# Start the dashboard proxy
kubectl proxy
```

Then access the dashboard at:
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/

Use the token from the previous step to log in.

## Troubleshooting

If you encounter issues during testing:

1. **Pods not starting**: Check pod status and logs
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Database connection issues**: Verify MongoDB service is running
   ```bash
   kubectl get svc mongodb
   kubectl describe svc mongodb
   ```

3. **Image pull failures**: Verify image is available in Minikube
   ```bash
   minikube image ls | grep cougarwise
   ```

4. **Ingress not routing traffic**: Check ingress controller
   ```bash
   kubectl get ingress
   kubectl describe ingress cougarwise-ingress
   ```

5. **Configuration issues**: Verify the ConfigMap is correctly applied
   ```bash
   kubectl get configmap cougarwise-config
   kubectl describe configmap cougarwise-config
   ```

## Testing Results

The Kubernetes deployment has been successfully tested with the following components:

1. **Backend API**: Deployed with 3 replicas for load balancing
2. **MongoDB**: Running with persistent storage
3. **Ingress**: Configured for external access

**Note on Health Checks**: For the initial deployment test, the health checks were disabled in `deployment.yaml` since there was no `/api/health` endpoint implemented. To enable health checks:

1. Implement a health check endpoint in your backend application:
   ```python
   @app.get("/api/health")
   def health_check():
       return {"status": "healthy"}
   ```

2. Uncomment the liveness and readiness probe sections in `deployment.yaml`

The current deployment is functional without health checks, but implementing them is recommended for production use to ensure automatic pod recovery and proper load balancing. 