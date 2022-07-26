import urllib.request
import datetime
import os
import icone as icone_raw_translator
from icone_translator import wzdx_creator
import json
import date_tools

ICONE_USERNAME = 'cdot'
ICONE_FILE_PATH = 'incidents-extended.xml'
ICONE_PASSWORD = 'icone_cdot'


url = "ftp://{usr}:{pwd}@iconetraffic.com:42663/{path}"


def get_ftp_file_contents():
    # format URL with username, password, and file path
    formatted_url = url.format(
        usr=ICONE_USERNAME, pwd=ICONE_PASSWORD, path=ICONE_FILE_PATH)

    # Download and decode file to string
    file_contents = urllib.request.urlopen(
        formatted_url).read().decode('utf-8-sig')

    return file_contents


now = datetime.datetime.now()
date_directory = now.strftime("%Y_%m_%d")
directories = [date_directory, f'{date_directory}/raw',
               f'{date_directory}/standard', f'{date_directory}/wzdx']
for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)

icone = get_ftp_file_contents()

with open(f'{date_directory}/raw/raw_{now.strftime("%Y%m%d-%H%M%S")}.xml', 'w', newline='') as f:
    f.write(icone)

    # 40 18 36 N
    # 104 59 11 west

standard_msgs = icone_raw_translator.generate_standard_messages_from_string(
    icone)

with open(f'{date_directory}/standard/standard_{now.strftime("%Y%m%d-%H%M%S")}.json', 'w', newline='') as f:
    f.write(json.dumps(standard_msgs, indent=2))

wzdx = {}
for standard in standard_msgs:
    print(f"ID: {standard['event']['source']['id']}, update_time: {date_tools.datetime_from_unix(standard['event']['source']['last_updated_timestamp']).strftime('%Y-%m-%dT%H:%M:%SZ')}, state: {standard['event']['additional_info']['devices'][0]['details']['status']['@state']}")

    wzdx_feature = wzdx_creator(standard)
    if not wzdx_feature:
        continue

    if not wzdx:
        wzdx = wzdx_feature
    else:
        wzdx['features'].extend(wzdx_feature['features'])

with open(f'{date_directory}/wzdx/wzdx_{now.strftime("%Y%m%d-%H%M%S")}.geojson', 'w', newline='') as f:
    f.write(json.dumps(wzdx, indent=2))
