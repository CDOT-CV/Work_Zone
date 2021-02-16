# iCone translator Cloud Function

A system was created in google cloud platform to automatically translate iCone data to WZDx message. This system consists of two pubsub topics and a cloud function.
A cloud scheduler automatically sends a message to a pubsub topic which triggers the cloud function. The cloud function retrieves iCone data from an ftp server (ftp://iconetraffic.com:42663) and translates to WZDx message.
It validates the WZDx message with json schema and publishes the message to a pubsub topic.

![alt text](iCone%20Translator%20block%20diagram.png)

## files present
cloud funtion files
- icone_translator.py
  - This file is currently located in translator/source_code/icone_translator.py
- main.py  
- requirements.txt
- wzdx_schema.json

## Environment Setup

Runtime Environment Variables

| Name      | Value | Description    |
| :---        |    :----:   |          ---: |
| icone_ftp_username_secret_name     | icone_ftp_username       |  name of secret containing iCone ftp server username  |
| icone_ftp_password_secret_name   | icone_ftp_password       | name of secret containing iCone ftp server password
| ftp_server_address   | iconetraffic.com        | iCone ftp server address     |
| ftp_port   | 42663       | iCone ftp server port number      |
| ftp_icone_file_path   | incidents.xml      | The icone filename in ftp server       |
| project_id   | cdot-cv-ode-dev        | gcp project id        |
| wzdx_topic_id   | wzdx_messages        | topic id for wzdx pub/sub topic      |

GCP Secrets

| Name       | Description     |
| :---           |          ---: |
| icone_ftp_username     |  icone ftp server username   |
| icone_ftp_password      | icone ftp server password      |


documentation file

- iCone_Translator block diagram.png
- README.md




 
   
  

