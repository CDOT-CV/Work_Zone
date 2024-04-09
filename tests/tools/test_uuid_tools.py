from wzdx.tools import uuid_tools


def test_random_uuid():
    uuid1 = uuid_tools.random_uuid()
    uuid2 = uuid_tools.random_uuid()

    assert uuid_tools.is_valid_uuid(str(uuid1))
    assert uuid_tools.is_valid_uuid(str(uuid2))
    assert uuid1 != uuid2


def test_get_seeded_uuid():
    name1 = "OpenTMS-Event2843552682"
    name3 = "OpenTMS-Event2702170538"
    uuid1 = uuid_tools.named_uuid(name1)
    uuid2 = uuid_tools.named_uuid(name1)
    uuid3 = uuid_tools.named_uuid(name3)

    assert uuid_tools.is_valid_uuid(str(uuid1))
    assert uuid_tools.is_valid_uuid(str(uuid2))
    assert uuid_tools.is_valid_uuid(str(uuid3))
    assert uuid1 == uuid2
    assert uuid1 != uuid3

    assert str(uuid1) == "933bb8d1-a666-51a7-af72-4e9f0f53ddc3"
    assert str(uuid3) == "6a19d3c4-1710-5970-a563-946320fbfb0a"
