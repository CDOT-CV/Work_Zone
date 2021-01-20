# {'bucket': 'icone_files', 'contentType': 'image/jpeg', 'crc32c': 'ZO4N6A==', 'etag': 'CNu+up7tnu4CEAE=', 
# 'generation': '1610745138552667', 'id': 'icone_files/61862931_1039122999618882_7010636350885986304_o_1039122996285549.JPEG/1610745138552667', 
# 'kind': 'storage#object', 'md5Hash': 'yOlwCtFi0L/3GPe23rYGbw==', 
# 'mediaLink': 'https://www.googleapis.com/download/storage/v1/b/icone_files/o/61862931_1039122999618882_7010636350885986304_o_1039122996285549.JPEG?generation=1610745138552667&alt=media', 
# 'metageneration': '1', 'name': '61862931_1039122999618882_7010636350885986304_o_1039122996285549.JPEG',
#  'selfLink': 'https://www.googleapis.com/storage/v1/b/icone_files/o/61862931_1039122999618882_7010636350885986304_o_1039122996285549.JPEG',
#   'size': '447421', 'storageClass': 'STANDARD', 'timeCreated': '2021-01-15T21:12:18.552Z', 'timeStorageClassUpdated': '2021-01-15T21:12:18.552Z', 
#   'updated': '2021-01-15T21:12:18.552Z'}

import icone_translator
from gcloud import storage
import json
import xmltodict

def hello_gcs(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
    print(f"Processing file: {file['name']}.")
    print (event)
    client = storage.Client()
    bucket = client.get_bucket(event['bucket'])
    blob = bucket.blob(event['name'])
    icone_obj=xmltodict.parse(blob.download_as_string())
    info=icone_translator.initialize_info()
    wzdx_obj=icone_translator.wzdx_creator(icone_obj,info)
    print(json.dumps(wzdx_obj))
    client = storage.Client()
    bucket = client.get_bucket('wzdx_files')
    blob = bucket.blob('wzdx.geojson')
    blob.upload_from_string(json.dumps(wzdx_obj, indent=2))
    return
