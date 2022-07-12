wzdx_v40_schema_string = {
    "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/WZDxFeed.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "WZDx v4.0 WZDxFeed",
    "description": "The GeoJSON output of a WZDx feed data feed (v4.0)",
    "type": "object",
    "properties": {
        "road_event_feed_info": {
            "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/FeedInfo.json"
        },
        "type": {
            "description": "The GeoJSON type",
            "enum": [
                "FeatureCollection"
            ]
        },
        "features": {
            "description": "An array of GeoJSON Feature objects which represent WZDx road events",
            "type": "array",
            "items": {
                "allOf": [
                    {
                        "properties": {
                            "properties": {
                                "properties": {
                                    "core_details": {
                                        "properties": {
                                            "event_type": {
                                                "enum": [
                                                    "work-zone",
                                                    "detour"
                                                ]
                                            }
                                        },
                                        "required": [
                                            "event_type"
                                        ]
                                    }
                                },
                                "required": [
                                    "core_details"
                                ]
                            }
                        },
                        "required": [
                            "properties"
                        ]
                    },
                    {
                        "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/RoadEventFeature.json"
                    }
                ]
            }
        },
        "bbox": {
            "$ref": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/main/schemas/4.0/BoundingBox.json"
        }
    },
    "required": [
        "road_event_feed_info",
        "type",
        "features"
    ]
}
