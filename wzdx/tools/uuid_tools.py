import random
import uuid
import os


NAMESPACE_UUID = uuid.UUID(
    os.getenv("NAMESPACE_UUID", "00000000-0000-0000-0000-000000000000")
)


def random_uuid():
    return uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=5)


def named_uuid(name: str):
    return uuid.uuid5(NAMESPACE_UUID, name)


def named_uuid_string(name):
    return str(named_uuid(name))


# Only for testing
def is_valid_uuid(uuid_to_test, version=5):
    """
    Check if uuid_to_test is a valid UUID.

     Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

     Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

     Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test
