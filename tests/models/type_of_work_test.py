import json
from wzdx.models import type_of_work


def test_serialization():
    tow = type_of_work.TypeOfWork(
        type_name=type_of_work.WorkTypeName.BARRIER_WORK,
        is_architectural_change=True,
    )
    json_str = json.dumps(tow.to_dict())
    tow_from_json = type_of_work.TypeOfWork.from_json(json_str)
    assert tow == tow_from_json

    assert json_str == '{"type_name": "barrier-work", "is_architectural_change": true}'
