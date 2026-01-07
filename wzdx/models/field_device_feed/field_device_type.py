from typing_extensions import Literal

"""
The FieldDeviceType enumerated type enumerates all types of field devices described by the specification.

Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/FieldDeviceType.md
"""
FieldDeviceType = Literal[
    "arrow-board",
    "camera",
    "dynamic-message-sign",
    "flashing-beacon",
    "hybrid-sign",
    "location-marker",
    "traffic-sensor",
    "traffic-signal",
]
