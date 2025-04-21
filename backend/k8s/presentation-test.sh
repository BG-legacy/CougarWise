#!/bin/bash
# Presentation Test Script for CougarWise Kubernetes Deployment
# This script demonstrates the running components of the Kubernetes deployment

# Set strict error handling
set -e

# Color definitions for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}==========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==========================================${NC}\n"
}

# Function to print component status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Function to check if a command exists
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed. Please install it and try again.${NC}"
        exit 1
    fi
}

# Function to check if metrics server is available
check_metrics() {
    if kubectl get apiservice v1beta1.metrics.k8s.io &> /dev/null; then
        return 0
    else
        echo -e "${YELLOW}Warning: Metrics server is not available. Resource usage will not be shown.${NC}"
        return 1
    fi
}

# Function to cleanup port forwarding
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ ! -z "$PF_PID" ]; then
        kill $PF_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up trap for cleanup
trap cleanup EXIT

# Check for required commands
check_command kubectl
check_command minikube

echo -e "${YELLOW}Starting CougarWise Kubernetes Presentation Test${NC}"

# 1. Show Cluster Status
print_section "1. Kubernetes Cluster Status"
echo "Minikube Status:"
minikube status
echo -e "\nKubernetes Version:"
kubectl version --output=json | jq -r '.clientVersion.gitVersion'

# 2. Show Running Pods
print_section "2. Running Pods"
echo "All Pods in the Cluster:"
kubectl get pods -o wide --no-headers | sort -k1,1 | uniq
echo -e "\nPod Details:"
kubectl get pods -o custom-columns="NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName,IP:.status.podIP" --no-headers | sort -k1,1 | uniq

# 3. Show Deployments
print_section "3. Deployments"
echo "All Deployments:"
kubectl get deployments
echo -e "\nDeployment Details:"
kubectl get deployments -o custom-columns="NAME:.metadata.name,DESIRED:.spec.replicas,CURRENT:.status.availableReplicas,UP-TO-DATE:.status.updatedReplicas,AVAILABLE:.status.availableReplicas"

# 4. Show Services
print_section "4. Services"
echo "All Services:"
kubectl get services
echo -e "\nService Details:"
kubectl get services -o custom-columns="NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,PORT(S):.spec.ports[*].port"

# 5. Show Ingress
print_section "5. Ingress Configuration"
echo "Ingress Resources:"
kubectl get ingress
echo -e "\nIngress Details:"
kubectl describe ingress cougarwise-ingress

# 6. Show MongoDB Status
print_section "6. MongoDB Status"
echo "MongoDB Pod:"
kubectl get pods -l app=mongodb
echo -e "\nMongoDB Service:"
kubectl get service mongodb
echo -e "\nMongoDB Persistent Volume Claim:"
kubectl get pvc mongodb-pvc --no-headers

# 7. Show Backend API Status
print_section "7. Backend API Status"
echo "Backend Pod:"
kubectl get pods -l app=cougarwise-backend
echo -e "\nBackend Service:"
kubectl get service cougarwise-backend-service

# 8. Test API Access
print_section "8. Testing API Access"
echo "Setting up port forwarding to backend service..."
kubectl port-forward svc/cougarwise-backend-service 8000:8000 > /dev/null 2>&1 &
PF_PID=$!
sleep 5

echo "Testing API health endpoint..."
if curl -s http://localhost:8000/api/health | grep -q "status"; then
    echo -e "${GREEN}API is responding successfully!${NC}"
    echo "API Response:"
    curl -s http://localhost:8000/api/health | jq .
else
    echo -e "${RED}API health check failed!${NC}"
    echo -e "${YELLOW}Response from API:${NC}"
    curl -s http://localhost:8000/api/health || true
fi

# 9. Show Resource Usage
print_section "9. Resource Usage"
if check_metrics; then
    echo "Node Resource Usage:"
    kubectl top nodes
    echo -e "\nPod Resource Usage:"
    kubectl top pods
else
    echo -e "${YELLOW}Skipping resource usage metrics as metrics server is not available.${NC}"
    echo "To enable metrics, run: minikube addons enable metrics-server"
fi

# 10. Show Horizontal Pod Autoscaler Status
print_section "10. Autoscaling Status"
echo "Horizontal Pod Autoscaler:"
kubectl get hpa
echo -e "\nHPA Details:"
kubectl describe hpa cougarwise-backend-hpa

# 11. Show ConfigMaps
print_section "11. Configuration"
echo "ConfigMaps:"
kubectl get configmaps
echo -e "\nCougarWise ConfigMap:"
kubectl describe configmap cougarwise-config

# 12. Summary
print_section "12. Deployment Summary"
echo "Total Pods: $(kubectl get pods --no-headers | wc -l)"
echo "Total Services: $(kubectl get services --no-headers | wc -l)"
echo "Total Deployments: $(kubectl get deployments --no-headers | wc -l)"
echo "Total Ingress: $(kubectl get ingress --no-headers | wc -l)"

echo -e "\n${GREEN}Presentation Test Completed!${NC}"
echo "All components have been demonstrated." 