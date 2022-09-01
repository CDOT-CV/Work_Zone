from google.api import label_pb2 as ga_label
from google.api import metric_pb2 as ga_metric
from google.cloud import monitoring_v3

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/cdot-rtdh-dev"
descriptor = ga_metric.MetricDescriptor()
descriptor.type = "custom.googleapis.com/wzdx_rest_count"
descriptor.metric_kind = ga_metric.MetricDescriptor.MetricKind.GAUGE
descriptor.value_type = ga_metric.MetricDescriptor.ValueType.INT64
descriptor.description = "Number of messages returned from WZDx rest endpoint"

labels = ga_label.LabelDescriptor()
labels.key = "WZDxCount"
labels.value_type = ga_label.LabelDescriptor.ValueType.STRING
labels.description = "Count of WZDx messages in rest response"
descriptor.labels.append(labels)

descriptor = client.create_metric_descriptor(
    name=project_name, metric_descriptor=descriptor
)
print("Created {}.".format(descriptor.name))
