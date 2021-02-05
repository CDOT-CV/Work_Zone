# iCone translator Cloud Function

A system was created in google cloud platform to automatically translate iCone data to WZDx message. This system consists of two pubsub topics and a cloud function.
A cloud scheduler automatically sends a message to a pubsub topic which triggers the cloud function. The cloud function retrieves iCone data from an ftp server (ftp://iconetraffic.com:42663) and translates to WZDx message.
It validates the WZDx message with json schema and publishes the message to a pubsub topic.

![alt text](iCone%20Translator%20block%20diagram.png)

## files present
cloud funtion files
- icone_translator.py
- main.py  
- requirements.txt
- wzdx_schema.json

documentation file

- iCone_Translator block diagram.png
- README.md




 
   
  

