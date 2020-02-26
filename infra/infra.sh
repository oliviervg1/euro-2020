#!/usr/bin/env bash

set -exu

GCP_PROJECT="ovg-euro-2020"
REGION="europe-west2"
CLUSTER_NAME="euro-2020"
DOMAIN="euro-2020.oliviervg.com"

# Required env variables
: "${OAUTH2_CLIENT_ID:?Variable not set or empty}"
: "${OAUTH2_CLIENT_SECRET:?Variable not set or empty}"
: "${FLASK_SECRET_KEY:?Variable not set or empty}"
: "${FOOTBALL_API_KEY:?Variable not set or empty}"

# Create static IP
gcloud compute addresses create $CLUSTER_NAME --global \
    || echo "IP already exists!"

# Create cluster
gcloud beta container --project "${GCP_PROJECT}" clusters create "${CLUSTER_NAME}" \
    --region "${REGION}" \
    --release-channel "regular" \
    --machine-type "e2-standard-2" \
    --num-nodes "3" \
    --enable-stackdriver-kubernetes \
    --enable-ip-alias \
    --enable-autoscaling \
    --min-nodes "0" \
    --max-nodes "5" \
    --addons HorizontalPodAutoscaling,HttpLoadBalancing,CloudRun \
    --enable-autorepair \
    --identity-namespace "${GCP_PROJECT}.svc.id.goog" \
    || echo "Cluster already exists!"

# Wait for cluster to be fully available
sleep 60

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region europe-west2 --project $GCP_PROJECT

# Deploy sample app
kubectl patch cm config-domainmapping -n knative-serving -p '{"data":{"autoTLS":"Enabled"}}'
gcloud run deploy $CLUSTER_NAME \
    --image gcr.io/cloudrun/hello:latest \
    --memory=128Mi \
    --platform gke \
    --cluster $CLUSTER_NAME \
    --cluster-location $REGION
gcloud run domain-mappings create \
    --service $CLUSTER_NAME \
    --domain $DOMAIN \
    --platform gke \
    --cluster $CLUSTER_NAME \
    --cluster-location $REGION

# Apply modifications to cluster
kubectl apply -f istio-healthcheck.yaml
kubectl -n gke-system patch svc istio-ingress \
    --type=json -p="$(cat istio-ingress-patch.json)" \
    --dry-run=true -o yaml | kubectl apply -f -
kubectl apply -f ingress.yaml

# Wait for HTTPS ingress to be fully available
sleep 300

# Enable IAP on HTTPS ingress
gcloud compute backend-services update $(gcloud compute backend-services list | grep gke-system-istio-ingress | cut -d' ' -f1) \
    --global \
    --iap=enabled,oauth2-client-id=$OAUTH2_CLIENT_ID,oauth2-client-secret=$OAUTH2_CLIENT_SECRET
