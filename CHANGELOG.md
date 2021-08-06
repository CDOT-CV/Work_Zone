7/22/2021
- Created a tools directory (at root of translator) containing all shared code and all code that was not strictly related to a translator (general polygon and datetime manipulation)
- Removed source_code directory and placed all contained files at the root of translator
- Re-organized documentation
- Updated argument parsing to use `argparse`. Automatically generates help message.
  - Made required parameters positional
  - Added --version
- Refactored unit test naming/directory structure
- Added CHANGELOG.md

8/6/2021
- Created NavJoy 568 to WZDx translator
  - can parse GPS coordinates from linestrings and polygons
  - generates 2 work zones per message (1 for each direction in directionOfTraffic, ex: "East/West")
- Updated date_tools with new iso8601 parsing functions
- Updated unit tests throughout project, coverage is currently at 87%
- Tested all translators
- TODO: Navjoy 568 Translator: Support additional zones per message (streetNameFrom2, ...)