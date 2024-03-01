import pathlib
from setuptools import setup, find_packages

VERSION = "1.3.0"
DESCRIPTION = 'CDOT Work Zone WZDx Translators'
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="cdot-wzdx-translator",
    version=VERSION,
    author="CDOT",
    author_email="CDOT_rtdh_prod@state.co.us",
    description=DESCRIPTION,
    long_description=README,
    packages=find_packages(exclude=["tests", "icone_arrow_boards"]),
    install_requires=[
        'xmltodict==0.12.0',
        'orjson==3.6.8',
        'jsonschema',
        'python-dateutil',
        'shapely==1.8.0',
        'geopy',
        'pyproj',
        'numpy',
        'requests',
        'pytz',
        'regex'],

    keywords=['python', 'wzdx'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)