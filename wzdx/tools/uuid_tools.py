# https://nathanielknight.ca/articles/consistent_random_uuids_in_python.html

import random
import uuid


def random_uuid():
    return uuid.UUID(bytes=bytes(random.getrandbits(8) for _ in range(16)), version=4)


def get_seeded_uuid(seed_string):
    if seed_string != None:
        random.seed(seed_string)
    return random_uuid()


def get_seeded_uuid_string(seed_string):
    return str(get_seeded_uuid(seed_string))


# Only for testing
def is_valid_uuid(uuid_to_test, version=4):
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
