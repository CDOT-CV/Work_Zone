import urllib.request
import datetime
import os
from google.cloud import storage
import pytz
import json
import logging


def set_clients():
    global _storage_client

    _storage_client = storage.Client()


def get_path():
    # Parsing the date from the file name
    date = datetime.datetime.now(pytz.timezone("US/Mountain"))
    print(date)
    # Defining the path for GCS bucket
    date_name = f"year={date.strftime('%Y')}/month={date.strftime('%m')}/day={date.strftime('%d')}/raw_{date.strftime('%Y%m%d-%H%M%S')}.json"
    print(date_name)
    return date_name


def upload_logs(contents, path, bucket_name):
    try:
        bucket = _storage_client.bucket(bucket_name)
        blob = bucket.blob(path)

        # Checking if the file is already uploaded
        if blob.exists() == False and contents:
            blob.upload_from_string(contents)
            print(f"{path} uploaded to {bucket_name}")
        else:
            print(f"blob already exists for {path}))")
        return True
    except Exception as e:
        print(f"Error uploading log path: {str(path)} to bucket: {bucket_name}")
        print(str(e))
        return False


def get_wzdx_data(endpoint, apiKey):
    # format URL with username, password, and file path
    url = f"{endpoint}?apiKey={apiKey}"
    print(url)

    # Download and decode file to string
    file_contents = urllib.request.urlopen(url).read().decode("utf-8-sig")

    return file_contents


def compare_features(prod_feature, experimental_feature):
    diff = {}

    # compare properties of features
    properties_to_compare = [
        "start_date",
        "end_date",
        "work_zone_type",
        "reduced_speed_limit_kph",
    ]
    for property in properties_to_compare:
        if prod_feature["properties"].get(property) != experimental_feature[
            "properties"
        ].get(property):
            diff[f"properties/{property}"] = {
                "prod": prod_feature["properties"].get(property),
                "experimental": experimental_feature["properties"].get(property),
            }

    # compare core_details of features
    core_details_to_compare = ["description", "update_date"]
    for detail in core_details_to_compare:
        if prod_feature["properties"]["core_details"].get(
            detail
        ) != experimental_feature["properties"]["core_details"].get(detail):
            diff[f"properties/core_details/{detail}"] = {
                "prod": prod_feature["properties"]["core_details"].get(detail),
                "experimental": experimental_feature["properties"]["core_details"].get(
                    detail
                ),
            }

    # compare geometry
    if prod_feature["geometry"] != experimental_feature["geometry"]:
        diff["geometry"] = {
            "prod": prod_feature["geometry"],
            "experimental": experimental_feature["geometry"],
        }

    return diff


def compare_wzdx_experimental_prod(experimental: dict, prod: dict) -> dict:
    total_diff = {}
    prod_dict = {}
    for feature in prod.get("features", []):
        prod_dict[feature["properties"]["core_details"]["name"]] = feature

    for feature in experimental.get("features", []):
        key = feature["properties"]["core_details"]["name"]

        if not prod_dict.get(key):
            total_diff[key] = {
                "diff": "Feature not found in prod",
                "experimental": feature,
            }
            continue

        diff = compare_features(prod_dict.get(key), feature)
        if diff:
            total_diff[key] = {
                "diff": diff,
                "prod": prod_dict.get(key),
                "experimental": feature,
            }
        del prod_dict[key]

    # get remaining features, not found in experimental
    for k, remaining_feature in prod_dict.items():
        total_diff[k] = {
            "diff": "Feature not found in experimental",
            "prod": remaining_feature,
        }
    return total_diff


def get_log(entry):
    BUCKET_NAME = os.getenv("BUCKET_NAME")

    WZDX_PROD_ENDPOINT = os.getenv("WZDX_PROD_ENDPOINT")
    WZDX_EXPERIMENTAL_ENDPOINT = os.getenv("WZDX_EXPERIMENTAL_ENDPOINT")
    API_KEY = os.getenv("API_KEY")

    set_clients()
    path = get_path()

    try:
        prod = get_wzdx_data(WZDX_PROD_ENDPOINT, API_KEY)
        experimental = get_wzdx_data(WZDX_EXPERIMENTAL_ENDPOINT, API_KEY)
    except Exception as e:
        logging.error(f"Error getting WZDX data: {e}")
        raise e

    upload_logs(prod, f"prod/{path}", BUCKET_NAME)
    upload_logs(experimental, f"experimental/{path}", BUCKET_NAME)

    try:
        diff = compare_wzdx_experimental_prod(
            json.loads(experimental), json.loads(prod)
        )
    except Exception as e:
        logging.error(f"Error diffing prod and experimental data: {e}")
        raise e

    upload_logs(json.dumps(diff, default=str), f"diff/{path}", BUCKET_NAME)

    return "SUCCESS"
