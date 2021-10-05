wzdx_v31_schema_string = {
    "$id": "https://raw.githubusercontent.com/usdot-jpo-ode/wzdx/master/create-feed/schemas/wzdx_v3.1_feed.json",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "WZDx v3.1 Feed",
    "description": "The GeoJSON output of a WZDx v3.1 data feed",
    "type": "object",
    "properties": {
        "road_event_feed_info": {
            "$ref": "#/definitions/RoadEventFeedInfo"
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
                "$ref": "#/definitions/RoadEventFeature"
            }
        },
        "bbox": {
            "$ref": "#/definitions/BoundingBox"
        }
    },
    "required": [
        "road_event_feed_info",
        "type",
        "features"
    ],
    "definitions": {
        "BoundingBox": {
            "title": "GeoJSON Bounding Box",
            "description": "Information on the coordinate range for a Geometry, Feature (RoadEventFeature), or FeatureCollection (WZDxFeed)",
            "type": "array",
            "minItems": 4,
            "items": {
                "type": "number"
            }
        },
        "RoadEventFeedInfo": {
            "title": "Road Event Feed Information",
            "description": "Describes WZDx feed header information such as metadata, contact information, and data sources",
            "type": "object",
            "properties": {
                "publisher": {
                    "description": "The organization responsible for publishing the feed",
                    "type": "string"
                },
                "contact_name": {
                    "description": "The name of the individual or group responsible for the data feed",
                    "type": "string"
                },
                "contact_email": {
                    "description": "The email address of the individual or group responsible for the data feed",
                    "type": "string",
                    "format": "email"
                },
                "update_frequency": {
                    "description": "The frequency in seconds at which the data feed is updated",
                    "type": "integer",
                    "minimum": 1
                },
                "update_date": {
                    "description": "The UTC date and time when the data feed was last updated",
                    "type": "string",
                    "format": "date-time"
                },
                "version": {
                    "description": "The WZDx specification version used to create the data feed, in 'major.minor' format",
                    "type": "string",
                    "pattern": "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)$"
                },
                "license": {
                    "description": "The URL of the license that applies to the data in the WZDx feed. This *must* be the string \"https://creativecommons.org/publicdomain/zero/1.0/\"",
                    "enum": [
                        "https://creativecommons.org/publicdomain/zero/1.0/"
                    ]
                },
                "data_sources": {
                    "description": "A list of specific data sources for the road event data in the feed",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/RoadEventDataSource"
                    },
                    "minItems": 1
                }
            },
            "required": [
                "update_date",
                "version",
                "publisher",
                "data_sources"
            ]
        },
        "RoadEventDataSource": {
            "title": "Road Event Data Source",
            "description": "Describes information about a specific data source used to build the work zone data feed",
            "type": "object",
            "properties": {
                "data_source_id": {
                    "description": "Unique identifier for the organization providing work zone data",
                    "type": "string"
                },
                "organization_name": {
                    "description": "The name of the organization for the authoritative source of the work zone data",
                    "type": "string"
                },
                "contact_name": {
                    "description": "The name of the individual or group responsible for the data source",
                    "type": "string"
                },
                "contact_email": {
                    "description": "The email address of the individual or group responsible for the data source",
                    "type": "string",
                    "format": "email"
                },
                "update_frequency": {
                    "description": "The frequency in seconds at which the data source is updated",
                    "type": "integer",
                    "minimum": 1
                },
                "update_date": {
                    "description": "The UTC date and time when the data source was last updated",
                    "type": "string",
                    "format": "date-time"
                },
                "location_method": {
                    "$ref": "#/definitions/LocationMethod"
                },
                "location_verify_method": {
                    "description": "The method used to verify the accuracy of the location information",
                    "type": "string"
                },
                "lrs_type": {
                    "description": "Describes the type of linear referencing system used for the milepost measurements",
                    "type": "string"
                },
                "lrs_url": {
                    "description": "A URL where additional information on the LRS information and transformation information is stored",
                    "type": "string",
                    "format": "uri"
                }
            },
            "required": [
                "data_source_id",
                "organization_name",
                "location_method"
            ]
        },
        "LocationMethod": {
            "title": "Location Method Enumerated Type",
            "description": "The typical method used to locate the beginning and end of a work zone impact area",
            "enum": [
                "channel-device-method",
                "sign-method",
                "junction-method",
                "other",
                "unknown"
            ]
        },
        "RoadEventFeature": {
            "title": "Road Event Feature (GeoJSON Feature)",
            "description": "The container object for a WZDx road event; an instance of a GeoJSON Feature",
            "type": "object",
            "properties": {
                "road_event_id": {
                    "description": "A unique identifier issued by the data feed provider to identify the WZDx road event",
                    "type": "string"
                },
                "type": {
                    "description": "The GeoJSON object type; must be 'Feature'",
                    "enum": [
                        "Feature"
                    ]
                },
                "properties": {
                    "$ref": "#/definitions/RoadEvent"
                },
                "geometry": {
                    "oneOf": [
                        {
                            "$ref": "https://geojson.org/schema/LineString.json"
                        },
                        {
                            "$ref": "https://geojson.org/schema/MultiPoint.json"
                        }
                    ]
                },
                "bbox": {
                    "$ref": "#/definitions/BoundingBox"
                }
            },
            "oneOf": [
                {
                    "properties": {
                        "properties": {
                            "required": [
                                "road_event_id"
                            ]
                        }
                    }
                },
                {
                    "required": [
                        "road_event_id"
                    ]
                }
            ],
            "required": [
                "type",
                "properties",
                "geometry"
            ]
        },
        "RoadEvent": {
            "title": "Road Event",
            "description": "Describes an activity taking place along a road segment",
            "type": "object",
            "properties": {
                "data_source_id": {
                    "description": "Identifies the data source from which the road event data is sourced from",
                    "type": "string"
                },
                "event_type": {
                    "$ref": "#/definitions/EventType"
                },
                "relationship": {
                    "$ref": "#/definitions/Relationship"
                },
                "road_names": {
                    "description": "A list of publicly known names of the road on which the event occurs. This may include the road number designated by a jurisdiction such as a county, state or interstate (e.g. I-5, VT 133)",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                },
                "direction": {
                    "$ref": "#/definitions/Direction"
                },
                "beginning_cross_street": {
                    "description": "Name or number of the nearest cross street along the roadway where the event begins",
                    "type": "string"
                },
                "ending_cross_street": {
                    "description": "Name or number of the nearest cross street along the roadway where the event ends",
                    "type": "string"
                },
                "beginning_milepost": {
                    "description": "The linear distance measured against a milepost marker along a roadway where the event begins",
                    "type": "number",
                    "minimum": 0
                },
                "ending_milepost": {
                    "description": "The linear distance measured against a milepost marker along a roadway where the event ends",
                    "type": "number",
                    "minimum": 0
                },
                "beginning_accuracy": {
                    "$ref": "#/definitions/SpatialVerification"
                },
                "ending_accuracy": {
                    "$ref": "#/definitions/SpatialVerification"
                },
                "start_date": {
                    "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event begins (e.g. 2020-11-03T19:37:00Z)",
                    "type": "string",
                    "format": "date-time"
                },
                "end_date": {
                    "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event ends (e.g. 2020-11-03T19:37:00Z)",
                    "type": "string",
                    "format": "date-time"
                },
                "start_date_accuracy": {
                    "$ref": "#/definitions/TimeVerification"
                },
                "end_date_accuracy": {
                    "$ref": "#/definitions/TimeVerification"
                },
                "event_status": {
                    "$ref": "#/definitions/EventStatus"
                },
                "vehicle_impact": {
                    "$ref": "#/definitions/VehicleImpact"
                },
                "workers_present": {
                    "description": "A flag indicating that there are workers present in the road event",
                    "type": "boolean"
                },
                "reduced_speed_limit": {
                    "description": "The reduced speed limit posted within the road event",
                    "type": "integer",
                    "minimum": 0
                },
                "restrictions": {
                    "description": "Zero or more road restrictions applying to the road event",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/RoadRestriction"
                    },
                    "uniqueItems": True
                },
                "description": {
                    "description": "Short free text description of the road event",
                    "type": "string"
                },
                "creation_date": {
                    "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event was created (e.g. 2020-11-03T19:37:00Z)",
                    "type": "string",
                    "format": "date-time"
                },
                "update_date": {
                    "description": "The UTC date and time (formatted according to RFC 3339, Section 5.6) when the road event was last updated (e.g. 2020-11-03T19:37:00Z)",
                    "type": "string",
                    "format": "date-time"
                },
                "types_of_work": {
                    "description": "A list of the types of work being done in a road event",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/TypeOfWork"
                    }
                },
                "lanes": {
                    "description": "A list of individual lanes within a road event (roadway segment)",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Lane"
                    }
                },
                "road_event_id": {
                    "description": "***DEPRECATED*** A unique identifier issued by the data feed provider to identify the work zone project or activity",
                    "type": "string"
                },
                "road_number": {
                    "description": "***DEPRECATED*** The road number designated by a jurisdiction such as a county, state or interstate (e.g. I-5, VT 133)",
                    "type": "string"
                },
                "road_name": {
                    "description": "***DEPRECATED*** Publicly known name of the road on which the event occurs",
                    "type": "string"
                },
                "total_num_lanes": {
                    "description": "***DEPRECATED*** The total number of lanes associated with the road event",
                    "type": "integer",
                    "exclusiveMinimum": 0
                }
            },
            "anyOf": [
                {
                    "required": [
                        "road_name"
                    ]
                },
                {
                    "required": [
                        "road_names"
                    ]
                }
            ],
            "required": [
                "data_source_id",
                "direction",
                "beginning_accuracy",
                "ending_accuracy",
                "start_date",
                "end_date",
                "start_date_accuracy",
                "end_date_accuracy",
                "vehicle_impact"
            ]
        },
        "Relationship": {
            "title": "Relationship",
            "description": "Identifies both sequential and hierarchical relationships between road events and other entities. For example, a relationship can be used to link multiple road events to a common 'parent', such as a project or phase, or identify a sequence of road events",
            "type": "object",
            "properties": {
                "first": {
                    "description": "Indicates the first (can be multiple) road event in a sequence of road events by RoadEventFeature 'id'",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                },
                "next": {
                    "description": "Indicates the next (can be multiple) road event in a sequence of road events by RoadEventFeature 'id'",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                },
                "parents": {
                    "description": "Indicates entities that the road event with this relationship is a part of, such as a work zone project or phase. Values can but do not have to correspond to a WZDx entity",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                },
                "children": {
                    "description": "Indicates entities that are part of the road event with this relationship, such as a detour or piece of equipment. Values can but do not have to correspond to a WZDx entity",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                }
            }
        },
        "TypeOfWork": {
            "title": "Type of Work",
            "description": "A description of the type of work being done in a road event and an indication of if that work will result in an architectural change to the roadway",
            "type": "object",
            "properties": {
                "type_name": {
                    "$ref": "#/definitions/WorkTypeName"
                },
                "is_architectural_change": {
                    "description": "A flag indicating whether the type of work will result in an architectural change to the roadway",
                    "type": "boolean"
                }
            },
            "required": [
                "type_name"
            ]
        },
        "Lane": {
            "title": "Lane",
            "description": "An individual lane within a road event",
            "type": "object",
            "properties": {
                "order": {
                    "description": "The position (index) of the lane in sequence on the roadway, where '1' represents the left-most lane",
                    "type": "integer",
                    "minimum": 1
                },
                "status": {
                    "$ref": "#/definitions/LaneStatus"
                },
                "type": {
                    "$ref": "#/definitions/LaneType"
                },
                "lane_number": {
                    "description": "The number assigned to the lane to help identify its position. Flexible, but usually used for regular, driveable lanes",
                    "type": "integer",
                    "minimum": 1
                },
                "restrictions": {
                    "description": "A list of restrictions specific to the lane",
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/LaneRestriction"
                    }
                }
            },
            "required": [
                "status",
                "type",
                "order"
            ]
        },
        "LaneRestriction": {
            "title": "Lane Restriction",
            "description": "A lane-level restriction, including type and value",
            "type": "object",
            "properties": {
                "restriction_type": {
                    "$ref": "#/definitions/RoadRestriction"
                },
                "restriction_value": {
                    "type": "number"
                },
                "restriction_units": {
                    "$ref": "#/definitions/LaneRestrictionUnit"
                }
            },
            "required": [
                "restriction_type"
            ],
            "dependencies": {
                "restriction_value": [
                    "restriction_units"
                ]
            }
        },
        "EventType": {
            "title": "Road Event Type Enumerated Type",
            "description": "The type of WZDx road event",
            "enum": [
                "work-zone",
                "detour"
            ]
        },
        "Direction": {
            "title": "Direction Enumerated Type",
            "description": "The direction for a road event based on standard naming for US roads; indicates the direction the traffic flow regardless of the real heading angle",
            "enum": [
                "northbound",
                "eastbound",
                "southbound",
                "westbound"
            ]
        },
        "SpatialVerification": {
            "title": "Spatial Verification Enumerated Type",
            "description": "An indication of how a geographical coordinate was defined",
            "enum": [
                "estimated",
                "verified"
            ]
        },
        "TimeVerification": {
            "title": "Time Verification Enumerated Type",
            "description": "A measure of how accurate a date-time is",
            "enum": [
                "estimated",
                "verified"
            ]
        },
        "EventStatus": {
            "title": "Event Status Enumerated Type",
            "description": "The status of the road event",
            "enum": [
                "planned",
                "pending",
                "active",
                "completed",
                "cancelled"
            ]
        },
        "VehicleImpact": {
            "title": "Vehicle Impact Enumerated Type",
            "description": "The impact to vehicular lanes along a single road in a single direction",
            "enum": [
                "all-lanes-closed",
                "some-lanes-closed",
                "all-lanes-open",
                "alternating-one-way",
                "unknown"
            ]
        },
        "RoadRestriction": {
            "title": "Road Restriction Enumerated Type",
            "description": "The type of vehicle restriction on a roadway",
            "enum": [
                "no-trucks",
                "travel-peak-hours-only",
                "hov-3",
                "hov-2",
                "no-parking",
                "reduced-width",
                "reduced-height",
                "reduced-length",
                "reduced-weight",
                "axle-load-limit",
                "gross-weight-limit",
                "towing-prohibited",
                "permitted-oversize-loads-prohibited",
                "local-access-only"
            ]
        },
        "WorkTypeName": {
            "title": "Work Type Name Enumerated Type",
            "description": "A high-level text description of the type of work being done in a road event",
            "enum": [
                "maintenance",
                "minor-road-defect-repair",
                "roadside-work",
                "overhead-work",
                "below-road-work",
                "barrier-work",
                "surface-work",
                "painting",
                "roadway-relocation",
                "roadway-creation"
            ]
        },
        "LaneStatus": {
            "title": "Lane Status Enumerated Type",
            "description": "The status of the lane for the traveling public",
            "enum": [
                "open",
                "closed",
                "shift-left",
                "shift-right",
                "merge-left",
                "merge-right",
                "alternating-one-way",
                "alternating-flow"
            ]
        },
        "LaneType": {
            "title": "Lane Type Enumerated Type",
            "description": "An indication of the type of lane or shoulder",
            "enum": [
                "lane",
                "right-turning-lane",
                "left-turning-lane",
                "right-exit-lane",
                "left-exit-lane",
                "right-entrance-lane",
                "left-entrance-lane",
                "sidewalk",
                "bike-lane",
                "alternating-flow-lane",
                "shoulder",
                "hov-lane",
                "reversible-lane",
                "center-left-turn-lane",
                "left-lane",
                "right-lane",
                "middle-lane",
                "center-lane",
                "right-shoulder",
                "left-shoulder",
                "right-merging-lane",
                "left-merging-lane",
                "right-exit-ramp",
                "right-second-exit-ramp",
                "left-exit-ramp",
                "left-second-exit-ramp",
                "right-entrance-ramp",
                "right-second-entrance-ramp",
                "left-entrance-ramp",
                "left-second-entrance-ramp"
            ]
        },
        "LaneRestrictionUnit": {
            "title": "Lane Restriction Unit Enumerated Type",
            "description": "Units of measure used for the lane restriction value",
            "enum": [
                "feet",
                "inches",
                "centimeters",
                "pounds",
                "tons",
                "kilograms"
            ]
        }
    }
}
