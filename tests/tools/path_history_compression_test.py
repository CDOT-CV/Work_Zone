import json
from wzdx.tools import path_history_compression


def test_generage_compressed_path():
    wzdx = json.loads(
        open('./tests/data/path_compression_valid_path.json').read())
    path = wzdx['features'][0]['geometry']['coordinates']

    compressed = path_history_compression.generate_compressed_path(path)
    assert len(compressed) == 80
