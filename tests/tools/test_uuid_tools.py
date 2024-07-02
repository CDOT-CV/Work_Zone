from wzdx.tools import uuid_tools
from unittest.mock import MagicMock, patch
import os


def test_random_uuid():
    uuid1 = uuid_tools.random_uuid()
    uuid2 = uuid_tools.random_uuid()

    assert uuid_tools.is_valid_uuid(str(uuid1))
    assert uuid_tools.is_valid_uuid(str(uuid2))
    assert uuid1 != uuid2


@patch.dict(
    os.environ,
    {
        "NAMESPACE_UUID": "3f0bce7b-1e59-4be0-80cd-b5f1f3801708",
    },
)
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

    assert str(uuid1) == "5b74060c-1e7e-5e1e-bf43-ac00f3080bf0"
    assert str(uuid3) == "e1898e28-02fd-5057-9cf3-c6a40cb0d0d2"
