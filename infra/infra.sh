#!/usr/bin/env bash

set -exu

GCP_PROJECT="ovg-euro-2020"
REGION="europe-west2"
CLUSTER_NAME="euro-2020"

# Required env variables
: "${OAUTH2_CLIENT_ID:?Variable not set or empty}"
: "${OAUTH2_CLIENT_SECRET:?Variable not set or empty}"

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

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region europe-west2 --project $GCP_PROJECT

# Apply modifications to cluster
kubectl create secret generic $CLUSTER_NAME-oauth2 \
    --from-literal=client_id=$OAUTH2_CLIENT_ID \
    --from-literal=client_secret=$OAUTH2_CLIENT_SECRET \
    || echo "Secret already existst!"
kubectl apply -f istio-healthcheck.yaml
kubectl -n gke-system patch svc istio-ingress \
    --type=json -p="$(cat istio-ingress-patch.json)" \
    --dry-run=true -o yaml | kubectl apply -f -
kubectl apply -f ingress.yaml
