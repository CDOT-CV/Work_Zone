from wzdx.tools import uuid_tools


def test_random_uuid():
    uuid1 = uuid_tools.random_uuid()
    uuid2 = uuid_tools.random_uuid()

    assert uuid_tools.is_valid_uuid(str(uuid1))
    assert uuid_tools.is_valid_uuid(str(uuid2))
    assert uuid1 != uuid2


def test_get_seeded_uuid():
    seed1 = "OpenTMS-Event2843552682"
    seed3 = "OpenTMS-Event2702170538"
    uuid1 = uuid_tools.get_seeded_uuid(seed1)
    uuid2 = uuid_tools.get_seeded_uuid(seed1)
    uuid3 = uuid_tools.get_seeded_uuid(seed3)

    assert uuid_tools.is_valid_uuid(str(uuid1))
    assert uuid_tools.is_valid_uuid(str(uuid2))
    assert uuid_tools.is_valid_uuid(str(uuid3))
    assert uuid1 == uuid2
    assert uuid1 != uuid3
