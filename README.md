# Work_Zone

Work zone code and documentation for WZDx, iCone, etc. 

| Build | Quality Gate | Code Coverage |
| :---- | :----------: | ------------: |
|       |              |               |

# WZDX Translator

## Project Description
This is an open source, proof of concept solution for translating work zone data in the form of COtrip/Salesforce, iCone, and NavJOY messages to the standardized WZDx 3.1 format. This project was developed for CDOT. A unique translator has been developed for each of these message types. These translators read in the source message, parse out specific fields, and generate a WZDx 3.1 message. For more information on these message formats and the data mappings between these messages and the WZDx format, see the [documentation](wzdx/docs). sample_files are located [here](wzdx/sample_files). All these translators are built to run from the command line and from GCP cloud functions, hosted within the CDOT OIM WZDX environment, connected to the RTDH (real time data hub). For more information on cloud hosting, see [GCP_cloud_function](wzdx/GCP_cloud_function). 

## Installation
```
pip install wzdx-translator-jacob6838
```

### Prerequisites
Requires:

- Python 3.6 (or higher)

## Translators
This set of WZDx message translators is set up to be implemented in GCP with App Engines and Dataflows. It is also set up with raw, standard, and enhanced (WZDx) data feeds. This means that to take a raw icone document and generate a WZDx message, the raw icone xml document must first be converted to 1 or multiple standard json messages (based on CDOT RTDH specification), and then each standard message may be converted into a single WZDx message. The next step in the data flow is to combine all of the WZDx messages together using the combination script. The GCP layout for this is described in the Google Cloud Hosting section below

### Environment Setup
This code requires Python 3.6 or a higher version. If you haven’t already, download Python and pip. You can install the required packages by running the following command:

```
pip install -r requirements.txt
```

#### Environment variable
Please set up the following environment variable for your local computer before running the script.

Runtime Environment Variables:

| Name                 |          Value           |                                    Description |
| :------------------- | :----------------------: | ---------------------------------------------: |
| contact_name         |       Ashley Nylen       |                      name of WZDx feed contact |
| contact_email        | ashley.nylen@state.co.us |                     email of WZDx feed contact |
| issuing_organization |           CDOT           | name of the organization issuing the WZDx feed |

Example usage:
for mac computer run the following script to initialize the environment variable:

```
env_var.sh
```


### Execution for iCone translator

#### Raw to Standard Conversion
```
python -m wzdx.raw_to_standard.icone inputfile.json --outputDir outputDirectory
```

Example usage:

```
python -m wzdx.raw_to_standard.icone 'wzdx/sample_files/raw/icone/incident_short.xml'
```
#### Standard to WZDx Conversion
```
python -m wzdx.standard_to_enhanced.icone_translator inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m wzdx.standard_to_enhanced.icone_translator 'wzdx/sample_files/standard/icone/standard_icone_1245_1633444335.json' 
```

### Execution for COtrip translator
#### Run the translator script (from Work_Zone)
```
python -m wzdx.standard_to_enhanced.cotrip_translator inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m wzdx.standard_to_enhanced.cotrip_translator 'wzdx/sample_files/raw/cotrip/cotrip_1.json'
```

### Execution for NavJoy 568 translator
This translator reads in a NavJoy 568 speed reduction form and translates it into a WZDx message. Many of the 568 messages cover 2 directions of traffic, and are thus expanded into 2 WZDx messages, one for each direction. 

The NavJoy Work Zone feed is being translated into WZDx by NavJoy themselves, the source and WZDx example messages are located here: [Navjoy Sample Data](wzdx/sample%20files/navjoy_data)

#### Raw to Standard Conversion

```
python -m wzdx.raw_to_standard.navjoy_568 inputfile.json --outputDir outputDirectory
```

Example usage:

```
python -m wzdx.raw_to_standard.navjoy_568 'wzdx/sample_files/raw/navjoy/direction_test_2.json'
```
#### Standard to WZDx Conversion

```
python -m wzdx.standard_to_enhanced.navjoy_translator inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m wzdx.standard_to_enhanced.navjoy_translator 'wzdx/sample_files/standard/navjoy/standard_568_Form568-cb0fdaf0-c27a-4bef-aabd-442615dfb2d6_1638373455_westbound.json' 
```

### Execution for Combine_wzdx

#### Run the translator script (from Work_Zone/wzdx)

```
python combine_wzdx.py icone_wzdx_output_message_file cotrip_wzdx_output_message_file --outputFile outputfile.geojson
```

Example usage:

```
python combine_wzdx.py '../sample_files/enhanced/icone_wzdx_translated_output_message.geojson' '../sample_files/enhanced/cotrip_wzdx_translated_output_message.geojson'
```

### Unit Testing

#### Run the unit test for translator script (from root directory)

```
python -m pytest 'tests/' -v
```

Ensure you have your environment configured correctly (as described above).

### Message Combination Logic:

The `combine_wzdx` script file combines the output from the iCone and COtrip translators, based on overlapping geography, into a single improved WZDx message. The COtrip message set contains significantly more data, and is used as the base for this new combined message. The script then finds any geographically co-located messages from the iCone data set, pulls in the additional information (comprised of vehicle impact data and data sources) and publishes a new, combined WZDx message. Future state of this script will include additional data fields from the iCone data set as they become available.


## Google Cloud Hosting
All of the translators featured in this repo are hosted in the CDOT GCP Cloud as Dataflows. The workflow begins with App Engines which retrieve raw data and drop it onto raw pub/sub topics. These are picked up by the raw_to_standard translator running as a Dataflow pipeline, which drops the generated standard message(s) onto a standard topic. These are processed into valid WZDx messages by the enhanced Dataflow pipeline. The final step is to store all of the WZDx files in BigQuery, and combine them into one single WZDx data feed. 

![GCP Processing](wzdx/docs/CDOT%20WZDx%20translators%20-%20Processing.png)


## Build Python Package

Build
```
pip install build
python -m build
```

Upload (Requires PyPi account)
```
python -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
```

Import
```
pip install wzdx-translator-jacob6838
```

### Documentation

documentation for iCone to WZDx translator is located here: [docs](wzdx/docs)

### Guidelines

- Issues
  - Create issues using the SMART goals outline (Specific, Measurable, Actionable, Realistic and Time-Aware)
- PR (Pull Requests)
  - Create all pull requests from the master branch
  - Create small, narrowly focused PRs
  - Maintain a clean commit history so that they are easier to review

## Contact Information

Contact Name: Ashley Nylen
Contact Information: [ashley.nylen@state.co.us]

## Abbreviations

WZDx: Workzone Data Exchange
