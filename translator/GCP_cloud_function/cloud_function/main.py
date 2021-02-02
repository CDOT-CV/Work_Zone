import icone_translator
from gcloud import storage
import json
import xmltodict
import shutil
import urllib.request as request
from contextlib import closing
from google.cloud import pubsub_v1


server = 'iconetraffic.com'
port = '42663'
user = 'cdot'
password = 'icone_cdot'
filepath = 'incidents.xml'


ftpString = 'ftp://{0}:{1}@{2}:{3}/{4}'
ftpUrl = ftpString.format(user, password, server, port, filepath)


def hello_pubsub(event, context):


  icone_data=get_ftp_file(ftpUrl)
  icone_obj=parse_xml(icone_data)
  info=icone_translator.initialize_info()

  wzdx_obj=icone_translator.wzdx_creator(icone_obj,info)
  wzdx_schema=get_wzdx_schema('wzdx_schema.json')
  validation_result=icone_translator.validate_wzdx(wzdx_obj,wzdx_schema)
  # if not validation_result:
  #   print('validation failed! see previous messages for error messages')
  print(json.dumps(wzdx_obj))

  publisher = pubsub_v1.PublisherClient()
  topic_path = publisher.topic_path('cdot-cv-ode-dev', 'wzdx_messages')
  future=publisher.publish(topic_path,str.encode(json.dumps(wzdx_obj, indent=2)),origin='auto_icone_translator_ftp cloud function')
  print(future.result())
  return

def get_ftp_file(url) :
  with closing(request.urlopen(url)) as r:
    return r.read().decode('utf-8-sig')


def parse_xml(xml_string):
  return xmltodict.parse(xml_string)

def get_wzdx_schema(schema_file_name):
  return json.loads(open(schema_file_name,'r').read())


