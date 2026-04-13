from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails


class ArrowBoardPattern(str, Enum):
    """
    The ArrowBoardPattern enumerated type defines a list of options for the posted pattern on an ArrowBoard.

    If the arrow board pattern does not exactly match one of the values described, the closest pattern should be used.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/enumerated-types/ArrowBoardPattern.md
    """

    BLANK = "blank"  # No pattern; the board is not displaying anything.
    RIGHT_ARROW_STATIC = "right-arrow-static"  # Merge right represented by an arrow pattern (e.g. -->) that does not flash or move.
    RIGHT_ARROW_FLASHING = "right-arrow-flashing"  # Merge right represented by an arrow pattern (e.g. -->) that flashes on/off.
    RIGHT_ARROW_SEQUENTIAL = "right-arrow-sequential"  # Merge right represented by an arrow pattern (e.g. -->) that is displayed in a progressing sequence (e.g. > -> --> or - -- -->).
    RIGHT_CHEVRON_STATIC = "right-chevron-static"  # Merge right represented by a pattern of chevrons (e.g. >>>) that does not flash or move.
    RIGHT_CHEVRON_FLASHING = "right-chevron-flashing"  # Merge right represented by a pattern of chevrons (e.g. >>>) that flashes on/off.
    RIGHT_CHEVRON_SEQUENTIAL = "right-chevron-sequential"  # Merge right represented by a pattern of chevrons that is displayed in a progressing sequence.
    LEFT_ARROW_STATIC = "left-arrow-static"  # Merge left represented by an arrow pattern (e.g. <--) that does not flash or move.
    LEFT_ARROW_FLASHING = "left-arrow-flashing"  # Merge left represented by an arrow pattern (e.g. <--) that flashes on/off.
    LEFT_ARROW_SEQUENTIAL = "left-arrow-sequential"  # Merge left represented by an arrow pattern (e.g. <--) that is displayed in a progressing sequence (e.g. < <- <-- or - -- <--).
    LEFT_CHEVRON_STATIC = "left-chevron-static"  # Merge left represented by a pattern of chevrons (e.g. <<<) that does not flash or move.
    LEFT_CHEVRON_FLASHING = "left-chevron-flashing"  # Merge left represented by a pattern of chevrons (e.g. <<<) that flashes on/off.
    LEFT_CHEVRON_SEQUENTIAL = "left-chevron-sequential"  # Merge left represented by a pattern of chevrons that is displayed in a progressing sequence.
    BIDIRECTIONAL_ARROW_STATIC = "bidirectional-arrow-static"  # Split (merge left or right) represented by arrows pointing both left and right (e.g. <-->) that does not flash or move.
    BIDIRECTIONAL_ARROW_FLASHING = "bidirectional-arrow-flashing"  # Split (merge left or right) represented by arrows pointing both left and right (e.g. <-->) that flashes on/off.
    LINE_FLASHING = "line-flashing"  # A flashing line or bar (e.g. ---), indicating warning/caution, not a merge.
    DIAMONDS_ALTERNATING = "diamonds-alternating"  # An alternating display of two diamond shapes (e.g. ◇ ◇), indicating warning/caution, not a merge.
    FOUR_CORNERS_FLASHING = "four-corners-flashing"  # Four dots on the corners of the board which flash, indicating warning/caution, not a merge.
    UNKNOWN = "unknown"  # The arrow board pattern is not known.


class ArrowBoardCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["arrow-board"] = "arrow-board"


class ArrowBoard(BaseModel):
    """
    The ArrowBoard object describes an electronic, connected arrow board which can display
    an arrow pattern to direct traffic. Arrow boards are often placed at the beginning of a
    lane closure—thus knowing the location of an arrow board can assist in programmatically
    generating a WZDx road event with verified spatial information.

    The ArrowBoard is a type of field device; it has a :class:`core_details` property which
    contains the :class:`FieldDeviceCoreDetails` and exists within a :class:`FieldDeviceFeature`.

    Documentation: https://github.com/usdot-jpo-ode/wzdx/blob/develop/spec-content/objects/ArrowBoard.md
    """

    core_details: ArrowBoardCoreDetails = Field(
        alias="core_details",
        description="The core details of the field device that are shared by all types of field devices, not specific to arrow boards.",
    )
    pattern: ArrowBoardPattern = Field(
        alias="pattern",
        description="The current pattern displayed on the arrow board. Note this includes blank, which indicates that nothing is shown on the arrow board.",
    )
    is_in_transport_position: Optional[bool] = Field(
        default=None,
        alias="is_in_transport_position",
        description="A yes/no value indicating if the arrow board is in the stowed/transport position (true) or deployed/upright position (false).",
    )
