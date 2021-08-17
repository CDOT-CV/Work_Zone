from translator.tools import array_tools


# --------------------------------------------- dim ---------------------------------------------
def test_dim_3d():
    list_3_d = [
        [
            [
                -104.65225365171561,
                40.39393671703483
            ]
        ]
    ]
    expected = [1, 1, 2]
    actual = array_tools.dim(list_3_d)
    assert actual == expected


def test_dim_3d():
    list_3_d = [
        [
            1, 2, 3, 4
        ],
        [
            1, 2, 3, 4
        ],
    ]
    expected = [2, 4]
    actual = array_tools.dim(list_3_d)
    assert actual == expected


def test_dim_none():
    list_3_d = None
    expected = []
    actual = array_tools.dim(list_3_d)
    assert actual == expected


# --------------------------------------------- get_2d_list ---------------------------------------------
def test_get_2d_list_3d():
    list_3d = [
        [
            [
                -104.65225365171561,
                40.39393671703483
            ]
        ]
    ]
    expected = [
        [
            -104.65225365171561,
            40.39393671703483
        ]
    ]
    actual = array_tools.get_2d_list(list_3d)
    assert actual == expected


def test_get_2d_list_2d():
    list_3d = [
        [
            -104.65225365171561,
            40.39393671703483
        ]
    ]
    expected = [
        [
            -104.65225365171561,
            40.39393671703483
        ]
    ]
    actual = array_tools.get_2d_list(list_3d)
    assert actual == expected


def test_get_2d_list_1d():
    list_3d = [
        -104.65225365171561,
        40.39393671703483
    ]
    expected = None
    actual = array_tools.get_2d_list(list_3d)
    assert actual == expected


def test_get_2d_list_empty():
    list_3d = []
    expected = None
    actual = array_tools.get_2d_list(list_3d)
    assert actual == expected


def test_get_2d_list_none():
    list_3d = None
    expected = None
    actual = array_tools.get_2d_list(list_3d)
    assert actual == expected
