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
  if not user or not password:
    return None
  filepath = os.environ['ftp_icone_file_path']
  ftpString = 'ftp://{0}:{1}@{2}:{3}/{4}'
  ftpUrl = ftpString.format(user, password, server, port, filepath)
  return ftpUrl

def translate_newest_icone_to_wzdx(event, context):
  try:
    ftp_url=get_ftp_url()
    if not ftp_url:
      logging.error(RuntimeError('failed to get ftp url. Exiting Application!'))
      return 'failed to get ftp url. Exiting Application!', 500

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
  username_secret_name = os.environ.get('icone_ftp_username_secret_name')
  password_secret_name = os.environ.get('icone_ftp_password_secret_name')
  project_id = os.environ.get('project_id')
           
  if not username_secret_name or not password_secret_name or not project_id:
    return None, None
  request = {"name": f"projects/{project_id}/secrets/{username_secret_name}/versions/latest"}
  try:
    response = secret_client.access_secret_version(request)
  except:
    logging.error(RuntimeError('unable to get username from secret. Either the secret does not exist or there are no permissions!'))
    return None, None
  username = response.payload.data.decode("UTF-8")

  request = {"name": f"projects/{project_id}/secrets/{password_secret_name}/versions/latest"}
  try:
    response = secret_client.access_secret_version(request)
  except:
    logging.error(RuntimeError('unable to get password from secret. Either the secret does not exist or there are no permissions!'))
    return None, None
  password = response.payload.data.decode("UTF-8")

  return username,password


def unsupported_messages_callback(message):
  project_id = os.environ.get('project_id')
  unsupported_messages_topic_id = os.environ.get('unsupported_messages_topic_id')
  if not project_id or not unsupported_messages_topic_id:
    return False
  publisher = pubsub_v1.PublisherClient()
  topic_path = publisher.topic_path(project_id, unsupported_messages_topic_id)
  #publish unsupported messages into pub/sub topic
  try:
    future = publisher.publish(topic_path, str.encode(formatMessage(message)), origin='auto_icone_translator_ftp cloud function')
    #future=publisher.publish(topic_path,str.encode(json.dumps(message, indent=2)),origin='auto_icone_translator_ftp cloud function')
  except Exception as e:
    logging.error('failed to publish unsupported message to project_id: {:s}, topic_id: {:s}, error_message: {:s}'.format(project_id, unsupported_messages_topic_id, str(e)))
    return False
  print(future.result())
  return True

def formatMessage(message) -> str:
  message_type = [dict,list, tuple, str, int, float, bool, type(None)]
  if type(message) in message_type:
    msg = json.dumps(message, indent=2)  
  else:
    msg = str(message) 
  return msg
  



