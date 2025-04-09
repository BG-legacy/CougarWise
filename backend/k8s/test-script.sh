#!/bin/bash
# Kubernetes Testing Script for CougarWise Backend
# This script automates the testing of the Kubernetes deployment

# Set strict error handling
set -e

# Color definitions for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting CougarWise Kubernetes Test Script${NC}"

# Step 1: Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl not found. Please install kubectl.${NC}"; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo -e "${RED}minikube not found. Please install minikube.${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}docker not found. Please install docker.${NC}"; exit 1; }
echo -e "${GREEN}Prerequisites verified.${NC}"

# Step 2: Start minikube if not running
echo -e "\n${YELLOW}Ensuring minikube is running...${NC}"
if ! minikube status | grep -q "Running"; then
  echo "Starting minikube..."
  minikube start --driver=docker --cpus=2 --memory=4096
else
  echo "Minikube is already running."
fi
echo -e "${GREEN}Minikube is running.${NC}"

# Step 3: Build and load the Docker image
echo -e "\n${YELLOW}Building and loading Docker image...${NC}"
cd ../
echo "Building docker image: cougarwise-backend:latest"
docker build -t cougarwise-backend:latest .
echo "Loading image into minikube..."
minikube image load cougarwise-backend:latest
echo -e "${GREEN}Docker image built and loaded.${NC}"

# Step 4: Apply Kubernetes resources
echo -e "\n${YELLOW}Deploying application to Kubernetes...${NC}"
cd k8s
kubectl apply -k .
echo -e "${GREEN}Kubernetes resources applied.${NC}"

# Step 5: Wait for deployments to be ready
echo -e "\n${YELLOW}Waiting for deployments to be ready...${NC}"
echo "Waiting for MongoDB deployment..."
kubectl wait --for=condition=available deployment/mongodb --timeout=120s
echo "Waiting for CougarWise backend deployment..."
kubectl wait --for=condition=available deployment/cougarwise-backend --timeout=120s
echo -e "${GREEN}Deployments are ready.${NC}"

# Step 6: Check all resources
echo -e "\n${YELLOW}Checking Kubernetes resources...${NC}"
echo "Pods:"
kubectl get pods
echo -e "\nDeployments:"
kubectl get deployments
echo -e "\nServices:"
kubectl get svc
echo -e "\nConfigMaps:"
kubectl get configmaps
echo -e "\nPVCs:"
kubectl get pvc
echo -e "\nIngress:"
kubectl get ingress
echo -e "${GREEN}Resource check complete.${NC}"

# Step 7: Test API access
echo -e "\n${YELLOW}Testing API access...${NC}"
echo "Setting up port forwarding to backend service (will run in background)..."
kubectl port-forward svc/cougarwise-backend-service 8000:8000 &
PF_PID=$!
echo "Waiting for port-forward to establish..."
sleep 5

# Test API health endpoint
echo "Testing API health endpoint..."
if curl -s http://localhost:8000/api/health | grep -q "status"; then
  echo -e "${GREEN}API health check successful!${NC}"
else
  echo -e "${RED}API health check failed!${NC}"
fi

# Kill port-forward process
echo "Stopping port forwarding..."
kill $PF_PID 2>/dev/null || true

# Step 8: Test MongoDB connection
echo -e "\n${YELLOW}Testing MongoDB connection...${NC}"
MONGO_POD=$(kubectl get pods -l app=mongodb -o jsonpath='{.items[0].metadata.name}')
echo "MongoDB pod: $MONGO_POD"
echo "Attempting to connect to MongoDB..."
kubectl exec -it $MONGO_POD -- mongosh --eval "db.adminCommand('ping')" | grep -q "ok: 1" && \
  echo -e "${GREEN}MongoDB connection successful!${NC}" || \
  echo -e "${RED}MongoDB connection failed!${NC}"

# Step 9: Summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "CougarWise backend Kubernetes setup has been tested."
echo "If all tests passed, your deployment is working correctly."

# Ask if user wants to clean up
echo -e "\n${YELLOW}Clean up${NC}"
read -p "Do you want to clean up all deployed resources? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Cleaning up Kubernetes resources..."
  kubectl delete -k .
  echo -e "${GREEN}Resources cleaned up.${NC}"
  
  read -p "Do you want to stop minikube? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Stopping minikube..."
    minikube stop
    echo -e "${GREEN}Minikube stopped.${NC}"
  fi
else
  echo "Resources left running. You can clean up later with 'kubectl delete -k .'."
fi

echo -e "\n${GREEN}Test script completed.${NC}" 