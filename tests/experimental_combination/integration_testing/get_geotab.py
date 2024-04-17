import logging
import datetime
from wzdx.tools import cdot_geospatial_api

ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"
logging.basicConfig(
    level=logging.INFO, format="%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
)
l = logging.getLogger(__name__)


def get_route_info_geotab(geotab):
    start = cdot_geospatial_api.GeospatialApi().get_route_and_measure(
        geotab["geometry"]["coordinates"][0]
    )
    end = cdot_geospatial_api.GeospatialApi().get_route_and_measure(
        geotab["geometry"]["coordinates"][1]
    )
    if not start or not end:
        return None
    elif start["Route"] != end["Route"] or start["Measure"] == end["Measure"]:
        return None
    else:
        return {
            "route": start["Route"],
            "start_measure": start["Measure"],
            "end_measure": end["Measure"],
        }


def create_geotab_query(attenuator_ids, query_interval_minutes):
    queries = []
    now = datetime.datetime.now(datetime.timezone.utc)
    start = now
    if now.hour == 0 and now.minute < query_interval_minutes:
        start1 = now - datetime.timedelta(minutes=query_interval_minutes)
        end1 = start1.replace(minute=59, second=59, microsecond=99999)
        start2 = now.replace(minute=0, second=0, microsecond=0)
        end2 = now
        queries.append(
            {
                "year": start1.year,
                "month": start1.month,
                "day": start1.day,
                "startTimestamp": start1.strftime(ISO_8601_FORMAT_STRING),
                "endTimestamp": end1.strftime(ISO_8601_FORMAT_STRING),
            }
        )
        queries.append(
            {
                "year": start2.year,
                "month": start2.month,
                "day": start2.day,
                "startTimestamp": start2.strftime(ISO_8601_FORMAT_STRING),
                "endTimestamp": end2.strftime(ISO_8601_FORMAT_STRING),
            }
        )
    else:
        start = now - datetime.timedelta(minutes=query_interval_minutes)
        queries.append(
            {
                "year": now.year,
                "month": now.month,
                "day": now.day,
                "startTimestamp": start.strftime(ISO_8601_FORMAT_STRING),
                "endTimestamp": now.strftime(ISO_8601_FORMAT_STRING),
            }
        )
    query_where_format = '(year = {year} and month = {month} and day = {day} and rtdh_timestamp BETWEEN TIMESTAMP("{startTimestamp}") and TIMESTAMP("{endTimestamp}"))'
    query_where = " or ".join(
        [query_where_format.format(**query_params) for query_params in queries]
    )
    query_ids = " or ".join(
        [f'avl_location.vehicle.id2 = "{id}"' for id in attenuator_ids]
    )
    query_str = f"""
        SELECT *
        FROM `cdot-adap-prod.raw_from_rtdh_standard.geotab_avl_standard_v3` 
        where ({query_where}) 
        and ({query_ids})
    """
    l.debug(query_str)
    return query_str


def get_query_results(query_str, _bigquery_client):
    query_job = _bigquery_client.query(query_str)
    return list(query_job)


def get_recent_geotab(attenuator_ids, query_interval_minutes, _bigquery_client):
    query_str = create_geotab_query(attenuator_ids, query_interval_minutes)
    return [
        {
            "avl_location": i["avl_location"],
            "rtdh_message_id": i["rtdh_message_id"],
            "rtdh_timestamp": i["rtdh_timestamp"].strftime(ISO_8601_FORMAT_STRING),
        }
        for i in get_query_results(query_str, _bigquery_client)
    ]
