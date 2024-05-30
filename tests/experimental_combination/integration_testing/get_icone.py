import urllib.request
import os
import xml.etree.ElementTree as ET
from wzdx.raw_to_standard.icone import create_rtdh_standard_msg
from wzdx.tools import wzdx_translator

from wzdx.util.collections import PathDict


ICONE_USERNAME = os.getenv("ICONE_USERNAME")
ICONE_FILE_PATH = os.getenv("ICONE_FILE_PATH")
ICONE_PASSWORD = os.getenv("ICONE_PASSWORD")

url = "ftp://{usr}:{pwd}@iconetraffic.com:42663/{path}"


def get_ftp_file_contents():
    # format URL with username, password, and file path
    formatted_url = url.format(
        usr=ICONE_USERNAME, pwd=ICONE_PASSWORD, path=ICONE_FILE_PATH
    )

    # Download and decode file to string
    file_contents = urllib.request.urlopen(formatted_url).read().decode("utf-8-sig")

    return file_contents


def parse_xml_to_dict(xml_string):
    d = ET.fromstring(xml_string)
    return d


def main():
    raw = parse_xml_to_dict(get_ftp_file_contents())
    raw_lst = raw.findall("incident")
    standard_msgs = []
    for i in raw_lst:
        raw_str = ET.tostring(i, encoding="utf8")
        obj = wzdx_translator.parse_xml_to_dict(raw_str)
        standard = create_rtdh_standard_msg(PathDict(obj))
        standard_msgs.append(standard)
    return standard_msgs
