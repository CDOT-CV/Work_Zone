# iCone translator Cloud Function

A system was created in google cloud platform to automatically translate iCone data to WZDx message.This system consits of two buckets and a cloud function.
When a file is uploaded to the first bucket, the cloud function automatically downloads the file, translates to a WZDx message and uploads it to the second bucket.

![alt text](iCone_Translator%20block%20diagram%20.png)

## files present
cloud funtion files
- icone_translator.py
- main.py  
- requirements.txt
- wzdx_schema.json

documentation file

- iCone_Translator block diagram.png
- README.md




 
   
  

