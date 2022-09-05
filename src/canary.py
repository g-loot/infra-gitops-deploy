import os
import json
import sys
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
    # print("Kubernetes local config loaded")

with client.ApiClient() as api_client:
    # Create an instance of the API class
    api_instance = client.CustomObjectsApi(api_client)
    api_instance_event = client.CoreV1Api(api_client)
    group = 'flagger.app'  # str | The custom resource's group name
    version = 'v1beta1'  # str | The custom resource's version
    namespace = 'default'  # str | The custom resource's namespace
    # str | The custom resource's plural name. For TPRs this would be lowercase plural kind.
    plural = 'canaries'
    # str | If 'true', then the output is pretty printed. (optional)
    pretty = 'true'
    # bool | allowWatchBookmarks requests watch events with type \"BOOKMARK\". Servers that do not implement bookmarks may ignore this flag and bookmarks are sent at the server's discretion. Clients should not assume bookmarks are returned at any specific interval, nor may they assume the server will send any BOOKMARK event during a session. If this is not a watch, this field is ignored. If the feature gate WatchBookmarks is not enabled in apiserver, this field is ignored. (optional)
    allow_watch_bookmarks = True
    _continue = ''  # str | The continue option should be set when retrieving more results from the server. Since this value is server defined, kubernetes.clients may only use the continue value from a previous query result with identical query parameters (except for the value of continue) and the server may reject a continue value it does not recognize. If the specified continue value is no longer valid whether due to expiration (generally five to fifteen minutes) or a configuration change on the server, the server will respond with a 410 ResourceExpired error together with a continue token. If the kubernetes.client needs a consistent list, it must restart their list without the continue field. Otherwise, the kubernetes.client may send another list request with the token received with the 410 error, the server will respond with a list starting from the next key, but from the latest snapshot, which is inconsistent from the previous list results - objects that are created, modified, or deleted after the first list request will be included in the response, as long as their keys are after the \"next key\".  This field is not supported when watch is true. Clients may start a watch from the last resourceVersion value returned by the server and not miss any modifications. (optional)
    # str | A selector to restrict the list of returned objects by their fields. Defaults to everything. (optional)
    field_selector = ''
    # str | A selector to restrict the list of returned objects by their labels. Defaults to everything. (optional)
    label_selector = ''
    limit = 56  # int | limit is a maximum number of responses to return for a list call. If more items exist, the server will set the `continue` field on the list metadata to a value that can be used with the same initial query to retrieve the next set of results. Setting a limit may return fewer than the requested amount of items (up to zero items) in the event all requested objects are filtered out and kubernetes.clients should only use the presence of the continue field to determine whether more results are available. Servers may choose not to support the limit argument and will return all of the available results. If limit is specified and the continue field is empty, kubernetes.clients may assume that no more results are available. This field is not supported if watch is true.  The server guarantees that the objects returned when using continue will be identical to issuing a single list call without a limit - that is, no objects created, modified, or deleted after the first request is issued will be included in any subsequent continued requests. This is sometimes referred to as a consistent snapshot, and ensures that a kubernetes.client that is using limit to receive smaller chunks of a very large result can ensure they see all possible objects. If objects are updated during a chunked list the version of the object that was present at the time the first list result was calculated is returned. (optional)
    # str | When specified with a watch call, shows changes that occur after that particular version of a resource. Defaults to changes from the beginning of history. When specified for list: - if unset, then the result is returned from remote storage based on quorum-read flag; - if it's 0, then we simply return what we currently have in cache, no guarantee; - if set to non zero, then the result is at least as fresh as given rv. (optional)
    resource_version = ''
    # str | resourceVersionMatch determines how resourceVersion is applied to list calls. It is highly recommended that resourceVersionMatch be set for list calls where resourceVersion is set See https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions for details.  Defaults to unset (optional)
    resource_version_match = ''
    # int | Timeout for the list/watch call. This limits the duration of the call, regardless of any activity or inactivity. (optional)
    timeout_seconds = 56
    # bool | Watch for changes to the described resources and return them as a stream of add, update, and remove notifications. (optional)
    watcha = True
    name = "github-pipeline-service"
    w = watch.Watch()
    # for event in w.stream(api_instance.list_namespaced_custom_object,
    #                       group=group, version=version, plural=plural, namespace=namespace):
    #   #print(event["object"]["status"]["conditions"][0]["message"])
    #   #print(event["object"]["status"]["conditions"])
    #   print(json.dumps(event))
    # print(json.dumps(api_instance.get_namespaced_custom_object_status(group, version, namespace, plural, name)))
    # x = json.loads(api_instance.get_namespaced_custom_object_status(group, version, namespace, plural, name))
    # if x["status"]["conditions"][0]["reason"] == "Succeeded":
    #  print("x = true")

    for event in w.stream(api_instance_event.list_namespaced_event, namespace):
        if ((script_start_time - timedelta(minutes=2)) < event["object"].last_timestamp
                and event["object"].involved_object.kind == "Canary"
                and event["object"].involved_object.name == "github-pipeline-service"
            ):
            print(event["object"].message, flush=True)
            # if fail -> exit with error code
            # I think we need to do the list_namespaced_custom_object and check for upcoming messeges aswell hmhm idk what to do here run them pararell?
            if event["object"].message == "Promotion completed! Scaling down github-pipeline-service.default":
                x = api_instance.get_namespaced_custom_object_status(
                    group, version, namespace, plural, name)
                if x["status"]["conditions"][0]["reason"] == "Succeeded":
                    sys.exit(0)
            elif "Rolling back github-pipeline-service.default progress deadline exceeded canary deployment" in event["object"].message:
                print("Canary failed", flush=True)
                sys.exit(1)
