from concurrent.futures import thread
import os
import json
import sys
import threading

from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
from datetime import datetime, timezone, timedelta
from dateutil.tz import tzutc

# Get current time
script_start_time = datetime.now(timezone.utc).replace(tzinfo=tzutc())

# Use the in_cluster_config when deploying to k8s
if os.environ.get("ENV") == "DEV" or os.environ.get("ENV") == "PROD":
    config.load_incluster_config()
    # print("Kubernetes cluster config loaded")
else:
    config.load_kube_config()
    # print("Kubernetes local config loaded"


def get_canary_status():
    with client.ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = client.CustomObjectsApi(api_client)
        group = 'flagger.app'  # str | The custom resource's group name
        version = 'v1beta1'  # str | The custom resource's version
        namespace = 'default'  # str | The custom resource's namespace
        plural = 'canaries'

        for event in watch.Watch().stream(api_instance.list_namespaced_custom_object,
                                          group=group, version=version, plural=plural, namespace=namespace):
            if ((script_start_time - timedelta(minutes=2)) < datetime.strptime(event["object"]["status"]["lastTransitionTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=tzutc())
                    and event["object"]["metadata"]["name"] == "github-pipeline-service"
                    ):
                if event["object"]["status"]["phase"] == "Failed":
                    print("Canary failed")
                    os._exit(1)


def get_canary_events():
    with client.ApiClient() as api_client:
        api_instance_custom_object = client.CustomObjectsApi(api_client)
        api_instance_event = client.CoreV1Api(api_client)
        group = 'flagger.app'  # str | The custom resource's group name
        version = 'v1beta1'  # str | The custom resource's version
        namespace = 'default'  # str | The custom resource's namespace
        plural = 'canaries'
        name = "github-pipeline-service"

        for event in watch.Watch().stream(api_instance_event.list_namespaced_event, namespace):
            if ((script_start_time - timedelta(minutes=2)) < event["object"].last_timestamp
                    and event["object"].involved_object.kind == "Canary"
                    and event["object"].involved_object.name == "github-pipeline-service"
                    ):
                print(event["object"].message, flush=True)
                if event["object"].message == "Promotion completed! Scaling down github-pipeline-service.default":
                    event_canary = api_instance_custom_object.get_namespaced_custom_object_status(
                        group, version, namespace, plural, name)
                    if event_canary["object"]["status"]["phase"] == "Succeeded":
                        print("Canary Succeeded", flush=True)
                        os._exit(0)
                elif "Rolling back github-pipeline-service.default progress deadline exceeded canary deployment" in event["object"].message:
                    # Canary failed! Scaling down github-pipeline-service.default
                    # I think we need to do the list_namespaced_custom_object and check for upcoming messeges aswell hmhm idk what to do here run them pararell?
                    print("Canary failed", flush=True)
                    os._exit(1)


t1 = threading.Thread(target=get_canary_status)
t2 = threading.Thread(target=get_canary_events)


t1.start()
t2.start()
