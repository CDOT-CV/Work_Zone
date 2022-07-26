import datetime
import json
from dateutil import parser
from wzdx.raw_to_standard import planned_events
from wzdx.standard_to_enhanced import planned_events_translator

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"


def parse_datetime_from_iso_string(time_string):
    """Parse ISO string to datetime. Handles many different datetime formats"""
    if not time_string or type(time_string) != str:
        return None

    return parser.parse(time_string)


def get_iso_string_from_datetime(date):
    # This is added for unit test mocking (dt.datetime instead of just datetime)
    if (not date or type(date) != datetime.datetime):
        return None
    return date.astimezone(datetime.timezone.utc).strftime(ISO_8601_FORMAT_STRING)


work_times = [
    {
        'start_time': "2022-07-21T09:00:00.000-06:00",
        'end_time':   "2022-07-21T17:00:00.000-06:00",
        'tester': "Ken",
    },
    # {
    #     'start_time': "2022-07-20T14:00:00.000-06:00",
    #     'end_time':   "2022-07-20T16:00:00.000-06:00",
    #     'tester': "Ken",
    # },
    # {
    #     'start_time': "2022-07-21T15:00:00.000-06:00",
    #     'end_time':   "2022-07-21T17:00:00.000-06:00",
    #     'tester': "Andy",
    # },
    # {
    #     'start_time': "2022-07-25T14:00:00.000-06:00",
    #     'end_time':   "2022-07-25T16:00:00.000-06:00",
    #     'tester': "Ken",
    # },
    # {
    #     'start_time': "2022-07-26T15:00:00.000-06:00",
    #     'end_time':   "2022-07-26T17:00:00.000-06:00",
    #     'tester': "Andy",
    # },
    # {
    #     'start_time': "2022-07-27T14:00:00.000-06:00",
    #     'end_time':   "2022-07-27T16:00:00.000-06:00",
    #     'tester': "Ken",
    # },
    # {
    #     'start_time': "2022-07-28T15:00:00.000-06:00",
    #     'end_time':   "2022-07-28T17:00:00.000-06:00",
    #     'tester': "Andy",
    # },
]

with open(f'planned_events_20220719-200017.json', 'r') as f:
    planned_events_list = json.loads(f.read())
    for work_time in work_times:
        filtered = []
        wzdx = {}
        for i in planned_events_list:
            startTime = parse_datetime_from_iso_string(
                i['properties']['startTime'])
            endTime = parse_datetime_from_iso_string(
                i['properties']['clearTime'])
            startTestingTime = parse_datetime_from_iso_string(
                work_time['start_time'])
            endTestingTime = parse_datetime_from_iso_string(
                work_time['end_time'])
            if endTime > endTestingTime and startTime < startTestingTime:
                filtered.append(i)
                standard = planned_events.generate_rtdh_standard_message_from_raw_single(
                    i)
                wzdx_msg = planned_events_translator.wzdx_creator(standard)
                if not wzdx and wzdx_msg:
                    wzdx = wzdx_msg
                elif wzdx_msg:
                    wzdx['features'].append(wzdx_msg['features'][0])
                else:
                    print(f'Error creating wzdx for {i["properties"]["id"]}')

        open(f"planned_events_wzdx_{work_time['start_time'].replace(':', '')}_{work_time['tester']}.json",
             'w+').write(json.dumps(wzdx, indent=2))
