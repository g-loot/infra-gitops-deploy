#!/bin/bash
set –e

tag=$INPUT_TAG
name=$INPUT_NAME
image=eu.gcr.io/docker-registry-shared-cc74/$INPUT_IMAGE

cluster_name=$INPUT_CLUSTER_NAME
cluster_zone=$INPUT_CLUSTER_ZONE
cluster_project=$INPUT_CLUSTER_PROJECT

echo "Tag: $tag"
echo "Name: $name"
echo "Image: $image"

echo "Cluster name: $INPUT_CLUSTER_NAME"
echo "Cluster zone: $INPUT_CLUSTER_ZONE"
echo "Cluster project: $INPUT_CLUSTER_PROJECT"

#Auth to GCP
echo "$INPUT_GCP_KEY" | base64 -d > /tmp/google_credentials.json
gcloud auth activate-service-account --key-file /tmp/google_credentials.json

#Choose cluster
gcloud container clusters get-credentials "$cluster_name" --zone "$cluster_zone" --project "$cluster_project"

while true
do
  if [[ $(kubectl get deployment/$name -o yaml | grep "image: $image" | xargs) = "image: $image:$tag" ]] && [[ $(kubectl rollout status deployment/$name) = 'deployment "'$name'" successfully rolled out' ]]; then
    kubectl rollout status deployment/$name
    echo "Deployed with tag: $tag"
    break;
  else
    echo "Waiting for image..."
  fi
  sleep 2
done

python3 canary.py
