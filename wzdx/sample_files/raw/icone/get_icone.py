import urllib.request
import datetime
import os
import wzdx
import json

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
               f'{date_directory}/standard', f'{date_directory}/enhanced']
for dir in directories:
    if not os.path.exists(date_directory):
        os.makedirs(date_directory)

icone = get_ftp_file_contents()

with open(f'{date_directory}/raw/raw_{now.strftime("%Y%m%d-%H%M%S")}.xml', 'w', newline='') as f:
    f.write(icone)

standard_msgs = wzdx.raw_to_standard.icone.generate_standard_messages_from_string(
    icone)

with open(f'{date_directory}/standard/standard_{now.strftime("%Y%m%d-%H%M%S")}.xml', 'w', newline='') as f:
    f.write(json.dumps(standard_msgs), indent=2)

wzdx = wzdx.standard_to_enhanced.icone_translator.wzdx_creator(standard)

with open(f'{date_directory}/wzdx/wzdx_{now.strftime("%Y%m%d-%H%M%S")}.xml', 'w', newline='') as f:
    f.write(json.dumps(standard), indent=2)
