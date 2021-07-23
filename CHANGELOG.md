7/22/2021
- Created a tools directory (at root of translator) containing all shared code and all code that was not strictly related to a translator (general polygon and datetime manipulation)
- Removed source_code directory and placed all contained files at the root of translator
- Re-organized documentation
- Updated argument parsing to use `argparse`. Automatically generates help message.
  - Made required parameters positional
  - Added --version
- Refactored unit test naming/directory structure
- Added CHANGELOG.md
