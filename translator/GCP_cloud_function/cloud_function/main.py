import icone_translator
import json
import xmltodict
import urllib
from google.cloud import pubsub_v1
import os
from google.cloud import secretmanager
import logging
import jsonschema


def get_ftp_url():
  server = os.environ['ftp_server_address']
  port = os.environ['ftp_port']
  user,password=get_ftp_credentials()
  filepath = os.environ['ftp_icone_file_path']
  ftpString = 'ftp://{0}:{1}@{2}:{3}/{4}'
  ftpUrl = ftpString.format(user, password, server, port, filepath)
  return ftpUrl

def translate_newest_icone_to_wzdx(event, context):
  try:
    ftp_url=get_ftp_url()
    icone_data=get_ftp_file(ftp_url)
  except:
    logging.error(RuntimeError('failed to get ftp file. Exiting Application!'))
    return 'failed to get ftp file. Exiting Application!', 500
  icone_obj=parse_xml(icone_data)

  wzdx_obj=icone_translator.wzdx_creator(icone_obj, unsupported_message_callback=unsupported_messages_callback)
  wzdx_schema=get_wzdx_schema('wzdx_schema.json')
  if not icone_translator.validate_wzdx(wzdx_obj,wzdx_schema):
    logging.error(RuntimeError('WZDx message failed validation. Exiting Application !'))
    return 'WZDx message failed validation. Exiting Application !', 500
  print(json.dumps(wzdx_obj))

  publisher = pubsub_v1.PublisherClient()
  topic_path = publisher.topic_path(os.environ['project_id'], os.environ['wzdx_topic_id'])
  future=publisher.publish(topic_path,str.encode(json.dumps(wzdx_obj, indent=2)),origin='auto_icone_translator_ftp cloud function')
  print(future.result())
  return

def get_ftp_file(url) :
  return urllib.request.urlopen(url).read().decode('utf-8-sig')

def parse_xml(xml_string):
  return xmltodict.parse(xml_string)

def get_wzdx_schema(schema_file_name):
  try:
    schema_string=open(schema_file_name,'r').read()
  except FileNotFoundError as e:
    raise RuntimeError('invalid schema: file does not exist')
  if not schema_string:
    raise RuntimeError('invalid schema: empty schema')
  try:
    schema_obj= json.loads(schema_string)
    jsonschema.validate('', schema_obj)  
  except json.decoder.JSONDecodeError as e :
    raise RuntimeError('invalid schema: not valid json') from e
  except jsonschema.SchemaError as e :
    raise RuntimeError('invalid schema: schema failed validation') from e
  except jsonschema.ValidationError:
    return schema_obj
  return schema_obj

def get_ftp_credentials():
  secret_client = secretmanager.SecretManagerServiceClient()
  username_secret_name = os.environ['icone_ftp_username_secret_name']
  password_secret_name = os.environ['icone_ftp_password_secret_name']
  project_id = os.environ['project_id']
  request = {"name": f"projects/{project_id}/secrets/{username_secret_name}/versions/latest"}
  response = secret_client.access_secret_version(request)
  username = response.payload.data.decode("UTF-8")

  request = {"name": f"projects/{project_id}/secrets/{password_secret_name}/versions/latest"}
  response = secret_client.access_secret_version(request)
  password = response.payload.data.decode("UTF-8")

  return username,password


def unsupported_messages_callback(message):
  #update this so that this code will execute once, not everytime the function is called
  publisher = pubsub_v1.PublisherClient()
  topic_path = publisher.topic_path(os.environ['project_id'], os.environ['unsupported_messages_topic_id'])
  #publish unsupported messages into pub/sub topic
  try:
    future=publisher.publish(topic_path,str.encode(json.dumps(message, indent=2)),origin='auto_icone_translator_ftp cloud function')
  except:
    future=publisher.publish(topic_path,str.encode(str(message)),origin='auto_icone_translator_ftp cloud function')
    
  print(future.result())
  raise RuntimeError('exiting testing !')
  return
  
  


