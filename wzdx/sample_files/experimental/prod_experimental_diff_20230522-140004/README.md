# Experimental iCone Message Example

This directory contains the results of using the wzdx.experimental_combination.icone script to combine an iCone arrow board with a planned event. The comparison was completed using the wzdx.monitoring.experimental.main script.

Scenario:
The start_date of a planned event was moved up in time because the arrow board indicated that work had begin before the planned start time. To learn more about this process, see the main [README.md](../../../../README.md)

Included files:

- diff_20230522-140004.json
  - Difference file between the planned-event only WZDx message and the icone-enhanced WZDx message. The "diff" field shows the individual properties that changed
- experimental_20230522-174002.json
  - Experimental icone-modified WZDx message
- prod_20230522-174002.json
  - Production WZDx message
- icone_20230522-164000.xml
  - iCone arrow board which was combined
