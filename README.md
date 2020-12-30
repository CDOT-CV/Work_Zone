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
   
  
## Environment Setup

This code requires Python 3.6 or a higher version. If you haven’t already, download Python and Pip. Next, you’ll need to install several packages that we’ll use throughout this tutorial. You can do this by opening terminal or command prompt on your operating system:


### Execution

#### Step 1: Run the translator script (from Work_Zone/translator/source code/Folder)

```
python icone_translator.py -i inputfile.xml -o outputfile.geojson
```


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

