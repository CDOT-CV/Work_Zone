import urllib.request
import datetime
import os
import xmltodict
import time
import re

# Here are the units for three of our patrol arrow boards:
# For the Two AAA ones:
# 13632784 00510
# 13632786 00511
#            Peak Period (0600-0930 & 1430-1900 M-F) – I-25 from 84th to Colfax
#             Off-peak Period (0930-1430 M-F) – I-25 from Baseline to 84th
#             Weekend (1000-1900 S-S) – I-25 from 84th to Speer

# And the R1 Maintenance TMA: (operations M-F, sometimes on the weekends if needed)
# 13632785 00512  - SH 83 from MM 74 to MM 62 and I25 MM 194 to 208

IDS = ['13632784', '13632786', '13632785']
#      U13632281_202210250517
ICONE_USERNAME = os.getenv('ICONE_USERNAME', 'cdot')
ICONE_FILE_PATH = os.getenv('ICONE_FILE_PATH', 'incidents-extended.xml')
ICONE_PASSWORD = os.getenv('ICONE_PASSWORD')

ICONE_URL = "ftp://{usr}:{pwd}@iconetraffic.com:42663/{path}"

QUERY_INTERVAL_SECONDS = 60 * 5  # 5 minutes


def main():
    startTime = time.time()
    startTimestamp = datetime.datetime.now()
    nameTimestamp = startTimestamp.strftime("%Y%m%d-%H%M%S")

    dir = startTimestamp.strftime("%Y_%m_%d")
    if not os.path.exists(dir):
        os.makedirs(dir)

    logFileName = f"{dir}/icone_log_{nameTimestamp}.txt"

    with open(logFileName, 'w+') as f:
        while True:
            icone = get_ftp_file_contents()
            nameTimestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            singleLogName = f"{dir}/icone_log_single_{nameTimestamp}.xml"

            with open(singleLogName, 'w', newline='') as sf:
                sf.write(icone)

            obj = parse_xml_to_dict(icone)
            icone_matches = [nameTimestamp]
            for incident in obj.get('incidents', {}).get('incident', []):
                id = incident['@id']
                if not match_id(id):
                    continue
                update_time = incident['updatetime']
                try:
                    state = incident['display']['status']['@state']
                except:
                    state = [i['@state']
                             for i in incident['display']['status']]
                update_time = incident['updatetime']
                msg = f"ID: {id}, update_time: {update_time}, state: {state}, polyline: {incident.get('location', {}).get('polyline')}"
                icone_matches.append(msg)
            f.write('; '.join(icone_matches))
            print(icone_matches)
            time.sleep((QUERY_INTERVAL_SECONDS -
                        ((time.time() - startTime) % QUERY_INTERVAL_SECONDS)))


def match_id(id):
    for ID in IDS:
        if re.search(f"U{ID}.*", id):
            return True
    return False


def get_ftp_file_contents():
    # format URL with username, password, and file path
    formatted_url = ICONE_URL.format(
        usr=ICONE_USERNAME, pwd=ICONE_PASSWORD, path=ICONE_FILE_PATH)

    # Download and decode file to string
    file_contents = urllib.request.urlopen(
        formatted_url).read().decode('utf-8-sig')

    return file_contents


def parse_xml_to_dict(xml_string):
    d = xmltodict.parse(xml_string)
    return d


if __name__ == '__main__':
    main()
