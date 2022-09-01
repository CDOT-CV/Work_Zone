import os
import json
import requests
import uuid
import time
from google.cloud import monitoring_v3

WZDX_REST_ENDPOINT_PROD = os.getenv(
    'WZDX_REST_ENDPOINT_PROD', 'https://data.cotrip.org/api/v1/wzdx?apiKey={api_key}')
WZDX_REST_API_KEY_PROD = os.getenv(
    'WZDX_REST_API_KEY_PROD', 'CT0E0KD-1S1MKYA-QSJ8WV7-045RH37')
WZDX_REST_ENDPOINT_TEST = os.getenv(
    'WZDX_REST_ENDPOINT_TEST', 'https://test.data.cotrip.org/api/v1/wzdx?apiKey={api_key}')
WZDX_REST_API_KEY_TEST = os.getenv(
    'WZDX_REST_API_KEY_TEST', 'CT0E0KD-1S1MKYA-QSJ8WV7-045RH37')
PROJECT_ID = os.getenv('PROJECT_ID', 'cdot-rtdh-dev')
PROD_METRIC_NAME = os.getenv(
    'PROD_METRIC_NAME', 'custom.googleapis.com/wzdx_rest_count')


def get_api_response(url, api_key):
    # format URL with username, password, and file path
    formatted_url = url.format(api_key=api_key)

    content = requests.get(formatted_url).content.decode("utf-8")
    # l.info(f"API Response content length: {len(content)}")

    return json.loads(content)


def write_metric(metric_name, value):
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"

    series = monitoring_v3.TimeSeries()
    series.metric.type = metric_name
    series.resource.type = "global"
    series.metric.labels["project"] = "cdot-rtdh-dev"
    series.metric.labels["host"] = "cloud-function"
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point(
        {"interval": interval, "value": {"int64_value": value}})
    series.points = [point]
    client.create_time_series(name=project_name, time_series=[series])


def main():
    prod_resp = get_api_response(
        WZDX_REST_ENDPOINT_PROD, WZDX_REST_API_KEY_PROD)
    prod_count = len(prod_resp['features'])
    print(prod_count)
    write_metric(PROD_METRIC_NAME, prod_count)

    test_resp = get_api_response(
        WZDX_REST_ENDPOINT_TEST, WZDX_REST_API_KEY_TEST)
    test_count = len(test_resp['features'])
    print(test_count)


if __name__ == '__main__':
    main()
