from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'CDOT Work Zone WZDx Translators'
LONG_DESCRIPTION = 'WZDx v3.1 translators from iCone, COTrip/Salesforce, and navjoy 568'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="wzdx-translator",
    version=VERSION,
    author="Jacob Frye",
    author_email="jfrye@neaeraconsulting.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(exclude=("wzdx")),
    install_requires=[
        'xmltodict',
        'jsonschema',
        'python-dateutil',
        'shapely',
        'geopy',
        'pyproj',
        'numpy',
        'requests',
        'pytz'],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'wzdx'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
