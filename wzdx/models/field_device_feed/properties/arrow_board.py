# device_feed/properties/arrow_board.py
from typing import Literal, Optional
from pydantic import BaseModel, Field
from enum import Enum
from ..field_device_core_details import FieldDeviceCoreDetails

class ArrowBoardPattern(str, Enum):
    BLANK = "blank"
    RIGHT_ARROW_STATIC = "right-arrow-static"
    RIGHT_ARROW_FLASHING = "right-arrow-flashing"
    RIGHT_CHEVRON_STATIC = "right-chevron-static"
    RIGHT_CHEVRON_FLASHING = "right-chevron-flashing"
    LEFT_ARROW_STATIC = "left-arrow-static"
    LEFT_ARROW_FLASHING = "left-arrow-flashing"
    LEFT_CHEVRON_STATIC = "left-chevron-static"
    LEFT_CHEVRON_FLASHING = "left-chevron-flashing"
    BIDIRECTIONAL_ARROW_STATIC = "bidirectional-arrow-static"
    BIDIRECTIONAL_ARROW_FLASHING = "bidirectional-arrow-flashing"
    FOUR_CORNERS_FLASHING = "four-corners-flashing"
    LINE_FLASHING = "line-flashing"
    DIAMONDS_ALTERNATING = "diamonds-alternating"
    BAR_FLASHING = "bar-flashing"
    UNKNOWN = "unknown"

class ArrowBoardCoreDetails(FieldDeviceCoreDetails):
    device_type: Literal["arrow-board"] = "arrow-board"

class ArrowBoard(BaseModel):
    core_details: ArrowBoardCoreDetails = Field(alias="core_details")
    pattern: Optional[ArrowBoardPattern] = None