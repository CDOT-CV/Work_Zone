import urllib.request
import datetime

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


with open(f'icone_ftp_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.xml', 'w+', newline='') as f:
    icone = get_ftp_file_contents()
    f.write(icone)
    print(icone)
