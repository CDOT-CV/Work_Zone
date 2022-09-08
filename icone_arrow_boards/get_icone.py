import urllib.request
import datetime
import os
import xmltodict

ICONE_USERNAME = os.getenv('ICONE_USERNAME')
ICONE_FILE_PATH = os.getenv('ICONE_FILE_PATH')
ICONE_PASSWORD = os.getenv('ICONE_PASSWORD')

print(ICONE_USERNAME, ICONE_FILE_PATH, ICONE_PASSWORD)

url = "ftp://{usr}:{pwd}@iconetraffic.com:42663/{path}"


def get_ftp_file_contents():
    # format URL with username, password, and file path
    formatted_url = url.format(
        usr=ICONE_USERNAME, pwd=ICONE_PASSWORD, path=ICONE_FILE_PATH)

    # Download and decode file to string
    file_contents = urllib.request.urlopen(
        formatted_url).read().decode('utf-8-sig')

    return file_contents


def parse_xml_to_dict(xml_string):
    d = xmltodict.parse(xml_string)
    return d


now = datetime.datetime.now()
date_directory = now.strftime("%Y_%m_%d")
directories = [date_directory, f'{date_directory}']
for dir in directories:
    if not os.path.exists(dir):
        os.makedirs(dir)

icone = get_ftp_file_contents()

with open(f'{date_directory}/raw_{now.strftime("%Y%m%d-%H%M%S")}.xml', 'w', newline='') as f:
    f.write(icone)

obj = parse_xml_to_dict(icone)
for incident in obj.get('incidents', {}).get('incident', []):
    id = incident['@id']
    update_time = incident['updatetime']
    try:
        state = incident['display']['status']['@state']
    except:
        state = [i['@state'] for i in incident['display']['status']]
    update_time = incident['updatetime']
    print(f"ID: {id}, update_time: {update_time}, state: {state}")
