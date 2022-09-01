import json
from wzdx.tools import path_history_compression


def test_generage_compressed_path():
    wzdx = json.loads(open('./tests/data/geotab_path_geo.json').read())
    path = wzdx['features'][0]['geometry']['coordinates']

    compressed = path_history_compression.generage_compressed_path(path)
    assert len(compressed) == 108
