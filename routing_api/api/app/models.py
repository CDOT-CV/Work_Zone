from pydantic import BaseModel, Field


class Route(BaseModel):
    route_id: str = Field(description="Route ID, like 070A")
    start_milepost: float = Field(description="Starting milepost")
    end_milepost: float = Field(description="Starting milepost")


class RouteWithGeometry(Route):
    geometry: list[list[float]] = Field(description="Route geometry, as long/lat")
    mileposts: list[float] = Field(
        description="Estimated mileposts along the route, indexed with the geometry"
    )


class PathRoutingRequest(BaseModel):
    from_route_id: str = Field(description="Route ID to start from")
    from_milepost: float = Field(description="Milepost to start from")
    to_route_id: str = Field(description="Route ID to end at")
    to_milepost: float = Field(description="Milepost to end at")
    include_geometry: bool = Field(
        False, description="Whether to include route geometry"
    )


class NavigationPathSegment(BaseModel):
    route_id: str = Field(description="Route ID of the segment, like 070A")
    start_milepost: float = Field(description="Starting milepost")
    end_milepost: float = Field(description="Ending milepost")


class NavigationPathSegmentWithGeometry(NavigationPathSegment):
    geometry: list[list[float]] = Field(description="Route geometry, as long/lat")
    mileposts: list[float] = Field(
        description="Estimated mileposts along the route, indexed with the geometry"
    )
