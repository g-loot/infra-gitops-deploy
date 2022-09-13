"""Script to see see progress of canary deployments"""
import os
import threading

from datetime import datetime, timezone, timedelta
from kubernetes import client, config, watch
from dateutil.tz import tzutc

# Get current time
script_start_time = datetime.now(timezone.utc).replace(tzinfo=tzutc())
name = os.environ.get("INPUT_NAME")  # Custom resource's name
namespace = os.environ.get("INPUT_NAMESPACE")  # Custom resource's namespace

GROUP = 'flagger.app'  # Custom resource's group name
VERSION = 'v1beta1'  # Custom resource's version
PLURAL = 'canaries'  # Custom resource's plural name


# Use the in_cluster_config when deploying to k8s
if os.environ.get("ENV") == "DEV" or os.environ.get("ENV") == "PROD":
    config.load_incluster_config()
    # print("Kubernetes cluster config loaded")
else:
    config.load_kube_config()
    # print("Kubernetes local config loaded"


def get_canary_status():
    """Get canary status. Exit program as sucess or failed depending if canary succeeds or fails"""
    with client.ApiClient() as api_client:
        api_instance = client.CustomObjectsApi(api_client)

        for event in watch.Watch().stream(api_instance.list_namespaced_custom_object,
                                          group=GROUP, version=VERSION, plural=PLURAL, namespace=namespace):
            # Check if the event is older than script_start_time minus 2 minutes to make sure we dont exit the script on old events
            if ((script_start_time - timedelta(minutes=2)) < datetime.strptime(event["object"]["status"]["lastTransitionTime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=tzutc())
                    and event["object"]["metadata"]["name"] == name
                    ):
                if event["object"]["status"]["phase"] == "Failed":
                    print("Canary failed", flush=True)
                    os._exit(1)
                elif event["object"]["status"]["phase"] == "Succeeded":
                    print("Canary succeeded", flush=True)
                    os._exit(0)


def get_canary_events():
    """Print canary events messages"""
    with client.ApiClient() as api_client:
        api_instance_event = client.CoreV1Api(api_client)
        # Check if the event is older than script_start_time minus 2 minutes to make sure we dont exit the script on old events
        for event in watch.Watch().stream(api_instance_event.list_namespaced_event, namespace):
            if ((script_start_time - timedelta(minutes=2)) < event["object"].last_timestamp
                    and event["object"].involved_object.kind == "Canary"
                    and event["object"].involved_object.name == name
                    ):
                print(event["object"].message, flush=True)


t1 = threading.Thread(target=get_canary_status)
t2 = threading.Thread(target=get_canary_events)

t1.start()
t2.start()
