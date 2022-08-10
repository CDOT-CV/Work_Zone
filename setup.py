import pathlib
from setuptools import setup, find_packages

VERSION = "1.1.2"
DESCRIPTION = 'CDOT Work Zone WZDx Translators'
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="cdot-wzdx-translator",
    version=VERSION,
    author="CDOT",
    author_email="CDOT_rtdh_prod@state.co.us",
    description=DESCRIPTION,
    long_description=README,
    packages=find_packages(exclude=["tests"]),
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
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
