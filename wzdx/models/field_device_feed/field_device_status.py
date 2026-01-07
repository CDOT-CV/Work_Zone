from enum import Enum


class FieldDeviceStatus(str, Enum):
    """
    The FieldDeviceStatus enumerated type describes the operational status of a field device. The status indicates the health of the device.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/FieldDeviceStatus.md
    """

    OK = "ok"  # The device is turned on and working without issue.
    WARNING = "warning"  # The device is functional but is impaired or impacted in a way that is not critical to operation.
    ERROR = "error"  # The device is impaired such that it is not able to perform one or more necessary functions.
    UNKNOWN = "unknown"  # The device's operational status is not known.
