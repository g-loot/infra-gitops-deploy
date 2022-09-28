#!/bin/bash
set –e

tag=$INPUT_TAG
name=$INPUT_NAME
image=eu.gcr.io/docker-registry-shared-cc74/$INPUT_IMAGE

cluster_name=$INPUT_CLUSTER_NAME
cluster_zone=$INPUT_CLUSTER_ZONE
cluster_project=$INPUT_CLUSTER_PROJECT

namespace=$INPUT_NAMESPACE
canary=$INPUT_CANARY

echo "Tag: $tag"
echo "Name: $name"
echo "Image: $image"
echo "Namespace: $INPUT_NAMESPACE"
echo "Canary: $INPUT_CANARY"

echo "Cluster name: $INPUT_CLUSTER_NAME"
echo "Cluster zone: $INPUT_CLUSTER_ZONE"
echo "Cluster project: $INPUT_CLUSTER_PROJECT"

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

if $canary; then
  echo "-----------CANARY STARTING-----------"
  python3 /infra-gitops-deploy/canary.py
fi
