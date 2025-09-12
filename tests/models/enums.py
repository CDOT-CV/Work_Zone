from wzdx.models.enums import EventType


def test_event_type():
    assert EventType.WORK_ZONE.value == "work-zone"
    assert EventType.DETOUR.value == "detour"
