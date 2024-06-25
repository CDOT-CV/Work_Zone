# Work_Zone

This is an open source, proof of concept solution for translating work zone data in the form of CDOT Planned Events, iCone device, and NavJOY 568 form data to the standardized [WZDx 4.2 format](https://github.com/usdot-jpo-ode/wzdx/tree/release/v4.2). This project was developed for CDOT. A unique translator has been developed for each of these message types. These translators read in the source message, parse out specific fields, and generate a WZDx message. For more information on these message formats and the data mappings between these messages and the WZDx format, see the [documentation](wzdx/docs). sample_files are located [here](wzdx/sample_files). All these translators are built to run from the command line and from GCP Dataflows, hosted within the CDOT RTDH WZDX environment. These translators are used to generate the CDOT Production WZDx data feed, which is published on the USDOT [WZDx Data Exchange Feed Registry](https://datahub.transportation.gov/Roadways-and-Bridges/Work-Zone-Data-Exchange-WZDx-Feed-Registry/69qe-yiui/data_preview)

The Google CloudPlatform deployment for the CDOT Planned Event WZDx translator is outlined below:
![GCP Planned Events](wzdx/docs/CDOT%20WZDx%20translators%20-%20Planned%20Events.png)

On top of these translators, combination scripts have been written to integrate WZDx messages from multiple separate sources, including CDOT Planned Events, iCone, and NavJOY. Each of these sources has unique data fields that are not present in the other sources, and the combination script is designed to merge these fields into a single WZDx message. The combination script is also built to run from the command line and from GCP Dataflows, hosted within the CDOT RTDH environment. The combination script is designed to run after the individual translators have generated their WZDx messages, and the output of the combination script is a single WZDx message that contains all of the data from the individual sources. When fields from multiple sources overlap, the combination script is designed to prioritize the data from the source with the most complete information. Geotab data is also integrated for mobile work zones, so that when a vehicle is detected in a "planned-moving-area" work zone, the work zone is changed to a "moving" work zone, using the current location of the vehicle plus a buffer distance ahead.

The Google CloudPlatform deployment for the CDOT WZDx combination workflow is outlined below:
![GCP Combination](wzdx/docs/CDOT%20WZDx%20translators%20-%20Processing.png)

## Building as a Package

This project is set up to be built into a python package, using python 3.8 and above. Use the following script to build the package:

```
pip install wheel
pip install -r requirements.txt
python setup.py sdist bdist_wheel
```

The build package tar.gz file will be located in the dist folder.

## Running the Translators Locally

This set of WZDx message translators is set up to be implemented in GCP with App Engines and Dataflows. It is also set up with raw, standard, and enhanced (WZDx) data feeds. This means that to take a raw icone document and generate a WZDx message, the raw icone xml document must first be converted to 1 or multiple standard json messages (based on CDOT RTDH specification), and then each standard message may be converted into a single WZDx message. At this point, this data can be combined with other WZDx messages, through the [combination scripts](wzdx/experimental_combination/)

### Prerequisites

Requires:

- Python 3.8 (or higher)

### Environment Setup

This code requires Python 3.8 or a higher version. If you haven’t already, download Python and pip. You can install the required packages by running the following command:

```
pip install -r requirements.txt
```

#### Environment variable

Please set up the following environment variable for your local computer before running the script.

Runtime Environment Variables:

| Name                         |                                                  Value                                                   |                                          Description |
| :--------------------------- | :------------------------------------------------------------------------------------------------------: | ---------------------------------------------------: |
| contact_name                 |                                        Heather Pickering-Hilgers                                         |                            name of WZDx feed contact |
| contact_email                |                                   heather.pickeringhilgers@state.co.us                                   |                           email of WZDx feed contact |
| publisher                    |                                                   CDOT                                                   |       name of the organization issuing the WZDx feed |
| CDOT_GEOSPATIAL_API_BASE_URL | https://dtdapps.colorado.gov/server/rest/services/LRS/Routes_withDEC/MapServer/exts/CdotLrsAccessRounded |          GIS server endpoint used for geospatial api |
| NAMESPACE_UUID               |                                   00000000-0000-0000-0000-000000000000                                   | UUID used to pseudo-randomly tag all UUIDs generated |

Example usage:
for mac computer run the following script to initialize the environment variable:

```
env_var.sh
```

### Execution for Translators

```
python -m wzdx.raw_to_standard.{raw translator} inputfile.json --outputDir outputDirectory
```

Example usage:

```
python -m wzdx.raw_to_standard.planned_events 'wzdx/sample_files/raw/planned_events/hwy_50.json'
```

#### Standard to WZDx Conversion

```
python -m wzdx.standard_to_enhanced.{standard translator} inputfile.json --outputFile outputfile.geojson
```

Example usage:

```
python -m wzdx.standard_to_enhanced.planned_events_translator 'wzdx/sample_files/standard/planned_events/standard_planned_event_OpenTMS-Event2702170538_eastbound.json'
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

### Combine WZDx Messages

These combination scripts take in a base WZDx message and an additional icone/navjoy WZDx or Geotab JSON message, and generate an enhanced WZDx message as output.

### iCone

Edit the files read in for iCone and WZDx messages in the main method, then run the combination script:

```
python icone.py wzdxFile.geojson ./iconeDirectory --outputDir ./ --updateDates true
```

### Navjoy 568 form

Edit the files read in for navjoy and WZDx messages in the main method, then run the combination script:

```
python navjoy.py wzdxFile.geojson navjoyWzdxFile.geojson --outputDir ./ --updateDates true
```

### Geotab Vehicle (ATMA)

Edit the files read in for geotab_avl and WZDx messages in the main method, then run the combination script:

```
python attenuator.py wzdxFile.geojson geotabFile.json --outputDir ./ --updateDates true
```

## Unit Testing

### Run the unit test for translator script (from root directory)

```
python -m pytest 'tests/' -v
```

Ensure you have your environment configured correctly (as described above).

### Unit Test Warnings

There are a few warnings shown by pypi, based on old package versions. These can be resolved by running the following commands:

```sh
pip install --upgrade google-cloud-storage==2.17.0
pip install --upgrade protobuf==5.27.1
```

### Unit Test Coverage

```
coverage run --source=wzdx -m pytest -v tests; coverage report -m
```

## Message Combination Logic:

The `combine_wzdx` script file combines the output from the iCone and Navjoy 568 translators, based on overlapping geography, into a single improved WZDx message. The CDOT planned events WZDx messages contain more accurate data, and are used as the base for the new combined message. The script then finds any geographically co-located messages from the iCone, Navjoy 568, and Geotab/AVL data sets, pulls in the additional information from each additional message, and generates a new, combined WZDx message.

## Documentation

documentation for the included WZDx translators are located here: [docs](wzdx/docs)

## Guidelines

- Issues
  - Create issues using the SMART goals outline (Specific, Measurable, Actionable, Realistic and Time-Aware)
- PR (Pull Requests)
  - Create all pull requests from the master branch
  - Create small, narrowly focused PRs
  - Maintain a clean commit history so that they are easier to review

## Contact Information

Contact Name: Heather Pickering-Hilgers
Contact Information: heather.pickeringhilgers@state.co.us

## Abbreviations

WZDx: Workzone Data Exchange
