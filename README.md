# Work_Zone
Work zone code and documentation for WZDx, iCone, etc.


| Build       | Quality Gate     | Code Coverage     |
| :------------- | :----------: | -----------: |
| [![Build Status](https://travis-ci.com/CDOT-CV/Work_Zone.svg?branch=dev)](https://travis-ci.com/CDOT-CV/Work_Zone)| [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?branch=dev&project=CDOT-CV_Work_Zone&metric=alert_status)](https://sonarcloud.io/dashboard?id=CDOT-CV_Work_Zone&branch=dev) | [![Coverage](https://sonarcloud.io/api/project_badges/measure?branch=dev&project=CDOT-CV_Work_Zone&metric=coverage)](https://sonarcloud.io/dashboard?id=CDOT-CV_Work_Zone&branch=dev)   |



# WZDX Translator

## Project Description

This project is an open source, proof of concept for Work Zone Data Exchange message creation from CDOT data to include iCone. The purpose of this tool is to  build a translator from CDOT work zone data and iCone data to the WZDx message (3.0). The message will contain required data by WZDx that can be populated by iCone and other CDOT Work Zone resources. Basically, in this project, we run a python script to parse data from the iCone xml file and other CDOT data which genrates WXDx 3.0 messages in a geojson format.

## Prerequisites

Requires:

- Python 3.6 (or higher)
  - xmltodict
  - jsonschema
  - shapely
   
  
## Environment Setup

This code requires Python 3.6 or a higher version. If you haven’t already, download Python and Pip. Next, you’ll need to install several packages that we’ll use throughout this tutorial. You can do this by opening terminal or command prompt on your operating system:

```
pip install -r requirements.txt
```



### Execution

#### Step 1: Run the translator script (from Work_Zone/translator/source code/Folder)

```
python icone_translator.py -i inputfile.xml -o outputfile.geojson
```
Example usage:
```
python icone_translator.py -i '../sample files/icone data/incidents_extended.xml' 
```

### Unit Testing


#### Run the unit test for translator script (from root directory)

```
$ python -m pytest 'test/' -v
```
Ensure you have your environment configured correctly (as described above).


### Google Cloud Function

A system was created in google cloud platform to automatically translate iCone data to WZDx message. This system consists of two pubsub topics and a cloud function. A cloud scheduler automatically sends a message to a pubsub topic which triggers the cloud function. The cloud function retrieves iCone data from an ftp server (ftp://iconetraffic.com:42663) and translates to WZDx message. It validates the WZDx message with json schema and publishes the message to a pubsub topic.


![alt text](translator/GCP_cloud_function/iCone%20Translator%20block%20diagram.png)

### Documentation

documentation for iCone to WZDx translator is located here: [docs](translator/docs)

### Guidelines

- Issues
  - Create issues using the SMART goals outline (Specific, Measurable, Actionable, Realistic and Time-Aware)
- PR (Pull Requests)
  - Create all pull requests from the master branch
  - Create small, narrowly focused PRs
  - Maintain a clean commit history so that they are easier to review
  
  
## Contact Information

Contact Name: Abinash Konersman
Contact Information: [abinash.konersman@state.co.us]

## Abbreviations

WZDx: Workzone Data Exchange

