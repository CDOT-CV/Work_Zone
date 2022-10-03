import json
from wzdx.tools import path_history_compression
import unittest


def test_get_chord_length():
    pt1 = [
        -105.02518638968468,
        39.776638166930375
    ]
    pt2 = [
        -105.02523601055145,
        39.771953483109826
    ]
    expected = 520  # https://boulter.com/gps/distance/?from=39.776638166930375%2C+-105.02518638968468&to=39.771953483109826%2C+-105.02523601055145&units=k
    actual = path_history_compression.getChordLength(pt1, pt2)

    testCase = unittest.TestCase()
    testCase.assertAlmostEqual(expected, actual, places=-1)


def test_generage_compressed_path():
    wzdx = json.loads(
        open('./tests/data/path_compression_valid_path.json').read())
    path = wzdx['features'][0]['geometry']['coordinates']

    compressed = path_history_compression.generate_compressed_path(path)
    assert len(compressed) == 80


def test_generage_compressed_path_empty():
    path = []

    compressed = path_history_compression.generate_compressed_path(path)
    assert len(compressed) == 0


def test_generage_compressed_path_short():
    path = [[], [], []]

    compressed = path_history_compression.generate_compressed_path(path)
    assert len(compressed) == 3
