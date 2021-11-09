import json
import jsonschema

msg = {'rtdh_timestamp': 1636143869.2708576, 'rtdh_message_id': 'ae6c34e5-56b0-48bb-916e-c37431458602', 'event': {'type': 'CONSTRUCTION', 'source': {'id': 1245, 'last_updated_timestamp': 1636163763}, 'geometry': [[-84.1238971, 37.1686478], [-84.1238971, 37.1686478], [-84.145861, 37.1913], [
    -84.145861, 37.1913], [-84.157105, 37.201197], [-84.167033, 37.206079], [-84.204074, 37.21931]], 'header': {'description': '19-1245: Roadwork between MP 40 and MP 48', 'start_timestamp': 1623204901, 'end_timestamp': None}, 'detail': {'road_name': 'I-75 N', 'road_number': 'I-75 N', 'direction': 'northbound'}}}

msg = json.loads(
    """{"rtdh_timestamp": 1636145176.7141519, "rtdh_message_id": "9d110390-ee88-42e9-b807-197fe8615485", "event": {"type": "CONSTRUCTION", "source": {"id": "1245", "last_updated_timestamp": 1636145042}, "geometry": [[-84.1238971, 37.1686478], [-84.1238971, 37.1686478], [-84.145861, 37.1913], [-84.145861, 37.1913], [-84.157105, 37.201197], [-84.167033, 37.206079], [-84.204074, 37.21931]], "header": {"description": "19-1245: Roadwork between MP 40 and MP 48", "start_timestamp": 1623183301, "end_timestamp": null}, "detail": {"road_name": "I-75 N", "road_number": "I-75 N", "direction": "northbound"}}}""")

schema = json.loads("""
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "properties": {
        "event": {
            "properties": {
                "detail": {
                    "properties": {
                        "direction": {
                            "type": ["string", "null"]
                        },
                        "road_name": {
                            "type": ["string", "null"]
                        },
                        "road_number": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": [
                        "road_name",
                        "road_number",
                        "direction"
                    ],
                    "type": "object"
                },
                "geometry": {
                    "items": [
                        {
                            "items": [
                                {
                                    "type": "number"
                                },
                                {
                                    "type": "number"
                                }
                            ],
                            "type": "array"
                        }
                    ],
                    "type": "array"
                },
                "header": {
                    "properties": {
                        "description": {
                            "type": "string"
                        },
                        "end_timestamp": {
                            "type": ["integer", "null"]
                        },
                        "start_timestamp": {
                            "type": "integer"
                        }
                    },
                    "required": [
                        "description",
                        "start_timestamp",
                        "end_timestamp"
                    ],
                    "type": "object"
                },
                "source": {
                    "properties": {
                        "id": {
                            "type": "integer"
                        },
                        "last_updated_timestamp": {
                            "type": "integer"
                        }
                    },
                    "required": [
                        "id",
                        "last_updated_timestamp"
                    ],
                    "type": "object"
                },
                "type": {
                    "type": "string"
                }
            },
            "required": [
                "type",
                "source",
                "geometry",
                "header",
                "detail"
            ],
            "type": "object"
        },
        "rtdh_message_id": {
            "type": "string"
        },
        "rtdh_timestamp": {
            "type": "number"
        }
    },
    "required": [
        "rtdh_timestamp",
        "rtdh_message_id",
        "event"
    ],
    "type": "object"
}""")

jsonschema.validate(msg, schema)
