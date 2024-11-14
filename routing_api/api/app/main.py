import datetime

from fastapi import FastAPI, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from models import (
    Route,
    RouteWithGeometry,
    PathRoutingRequest,
    PathRoutingRequestPoints,
    NavigationPathSegment,
    NavigationPathSegmentWithGeometry,
)

from navigator import NavigatorApi
from route_api import RouteApi

import os
import sys
import pytz
import json
import networkx as nx


ISO_8601_FORMAT_STRING = "%Y-%m-%dT%H:%M:%SZ"

API_VERSION = os.getenv("API_VERSION", 0.1)

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>",
)

app = FastAPI(summary="IMP Cloud API (Partner Backend)")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RouteGraph = nx.read_gml("./resources/route_graph.gml")
routes = json.load(open("./resources/routes_with_mile_markers.json"))
routes_dict = {route["Route"]: route for route in routes}

routeApi = RouteApi(routes_dict)
navigator = NavigatorApi(routes_dict, routeApi)


##################################################################
# Rest Endpoint
##################################################################
@app.get("/")
def read_root():
    logger.debug(
        f"Received request to / at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    return f"CDOT Graph Routing API, Version {API_VERSION}"


@app.get("/routes", description="Return a list of all available routes")
async def list_environments(
    route_ids: str = Query(
        None,
        description="Comma-separated list of route IDs to fetch. If empty, returns all",
    ),
    include_geometry: bool = Query(
        False, description="Whether to include route geometry"
    ),
) -> list[Route] | list[RouteWithGeometry]:
    logger.debug(
        f"Received request to /environments at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )

    filtered_routes = []
    if route_ids:
        for route in routes:
            if route["Route"] in route_ids:
                filtered_routes.append(route)
    else:
        filtered_routes.extend(routes)

    if include_geometry:
        return [
            RouteWithGeometry(
                route_id=route["Route"],
                start_milepost=route["MMin"],
                end_milepost=route["MMax"],
                geometry=route["Geometry"],
                mileposts=route["Distances"],
            )
            for route in filtered_routes
        ]
    else:
        return [
            Route(
                route_id=route["Route"],
                start_milepost=route["MMin"],
                end_milepost=route["MMax"],
            )
            for route in filtered_routes
        ]


@app.get("/routes/{route_id}", description="Return details for a specific route")
async def get_route_details(
    route_id: str,
) -> Route | RouteWithGeometry:
    logger.debug(
        f"Received request to /route/{route_id} at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    route = routeApi.get_route_details(route_id)
    if not route:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"Error": f"Route {route_id} not found"},
        )
    if route["Geometry"]:
        return RouteWithGeometry(
            route_id=route["Route"],
            start_milepost=route["MMin"],
            end_milepost=route["MMax"],
            geometry=route["Geometry"],
            mileposts=route["Distances"],
        )
    else:
        return Route(
            route_id=route["Route"],
            start_milepost=route["MMin"],
            end_milepost=route["MMax"],
        )


@app.get(
    "/routes/{route_id}/{measure}",
    description="Return the position of a point along a route",
)
async def get_point_at_measure(
    route_id: str,
    measure: float,
) -> list[float]:
    logger.debug(
        f"Received request to /route/{route_id}/{measure} at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    point = routeApi.get_point_at_measure(route_id, measure)
    if not point:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"Error": f"Route {route_id} not found"},
        )
    return point


@app.get(
    "/routes/{route_id}/{start_measure}/{end_measure}",
    description="Return the geometry of a route between two measures",
)
async def get_route_between_measures(
    route_id: str,
    start_measure: float,
    end_measure: float,
) -> list[list[float]]:
    logger.debug(
        f"Received request to /route/{route_id}/{start_measure}/{end_measure} at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    geometry = routeApi.get_route_between_measures(route_id, start_measure, end_measure)
    if not geometry:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"Error": f"Route {route_id} not found"},
        )
    return geometry


@app.get(
    "/closest-route",
    description="Return the route id and measure of the closest route to a point",
)
async def get_route_and_measure(
    lng: float = Query(description="Longitude, in degrees"),
    lat: float = Query(description="Latitude, in degrees"),
    threshold_meters: float = Query(10000, description="Maximum distance to search"),
) -> tuple[str, float, float, list[tuple[str, float]]]:
    logger.debug(
        f"Received request to /routes/closest at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    return routeApi.get_route_and_measure(lng, lat, threshold_meters)


@app.post(
    "/path", description="Return a navigation path between two routes and measures"
)
async def get_path(
    path_request: PathRoutingRequest,
) -> list[NavigationPathSegment]:
    logger.debug(
        f"Received request to /path at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    RouteGraphCopy = RouteGraph.copy()
    nav_routes = navigator.get_navigation_route(
        RouteGraphCopy,
        path_request.from_route_id,
        path_request.from_milepost,
        path_request.to_route_id,
        path_request.to_milepost,
    )
    if type(nav_routes) == str:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Error": nav_routes},
        )
    else:
        nav_routes = navigator.process_route(nav_routes)
        if path_request.include_geometry:
            path_segments = [
                NavigationPathSegmentWithGeometry(
                    route_id=route[0],
                    start_milepost=route[1],
                    end_milepost=route[2],
                    mileposts=[],
                    geometry=navigator.get_geometry([route]),
                )
                for route in nav_routes
            ]
        else:
            path_segments = [
                NavigationPathSegment(
                    route_id=route[0], start_milepost=route[1], end_milepost=route[2]
                )
                for route in nav_routes
            ]
        logger.warning(path_segments)
        return path_segments


@app.post(
    "/path-from-points",
    description="Return a navigation path between two points",
)
async def get_path_between_points(
    path_request: PathRoutingRequestPoints,
) -> list[NavigationPathSegment] | list[NavigationPathSegmentWithGeometry]:
    logger.debug(
        f"Received request to /path-from-points at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    start_route, start_measure, _, __ = routeApi.get_route_and_measure(
        path_request.start_lng, path_request.start_lat
    )
    end_route, end_measure, _, __ = routeApi.get_route_and_measure(
        path_request.end_lng, path_request.end_lat
    )
    if not start_route or not end_route:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "Error": f"Could not find routes for start ({start_route}) or end ({end_route})"
            },
        )
    RouteGraphCopy = RouteGraph.copy()
    nav_routes = navigator.get_navigation_route(
        RouteGraphCopy,
        start_route,
        start_measure,
        end_route,
        end_measure,
    )
    if type(nav_routes) == str:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Error": nav_routes},
        )
    else:
        nav_routes = navigator.process_route(nav_routes)
        if path_request.include_geometry:
            path_segments = [
                NavigationPathSegmentWithGeometry(
                    route_id=route[0],
                    start_milepost=route[1],
                    end_milepost=route[2],
                    mileposts=[],
                    geometry=navigator.get_geometry([route]),
                )
                for route in nav_routes
            ]
        else:
            path_segments = [
                NavigationPathSegment(
                    route_id=route[0], start_milepost=route[1], end_milepost=route[2]
                )
                for route in nav_routes
            ]
        return path_segments


@app.post(
    "/path-geojson", description="Return a list of all available environments, by name"
)
async def get_path_geojson(
    path_request: PathRoutingRequest,
) -> dict:
    logger.debug(
        f"Received request to /path-geojson at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    RouteGraphCopy = RouteGraph.copy()
    nav_routes = navigator.get_navigation_route(
        RouteGraphCopy,
        path_request.from_route_id,
        path_request.from_milepost,
        path_request.to_route_id,
        path_request.to_milepost,
    )
    if type(nav_routes) == str:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Error": nav_routes},
        )
    else:
        nav_routes = navigator.process_route(nav_routes)
        logger.warning(nav_routes)
        geojson = [
            {
                "type": "Feature",
                "properties": {
                    "route_id": route[0],
                    "start_milepost": route[1],
                    "end_milepost": route[2],
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": navigator.get_geometry([route]),
                },
            }
            for route in nav_routes
        ]
        return {"type": "FeatureCollection", "features": geojson}


@app.post(
    "/path-geojson-from-points",
    description="Return a navigation path between two points",
)
async def get_path_between_points(
    path_request: PathRoutingRequestPoints,
) -> dict:
    logger.debug(
        f"Received request to /path-geojson-from-points at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    start_route, start_measure, _, __ = routeApi.get_route_and_measure(
        path_request.start_lng, path_request.start_lat
    )
    end_route, end_measure, _, __ = routeApi.get_route_and_measure(
        path_request.end_lng, path_request.end_lat
    )
    if not start_route or not end_route:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "Error": f"Could not find routes for start ({start_route}) or end ({end_route})"
            },
        )
    RouteGraphCopy = RouteGraph.copy()
    nav_routes = navigator.get_navigation_route(
        RouteGraphCopy,
        start_route,
        start_measure,
        end_route,
        end_measure,
    )
    if type(nav_routes) == str:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Error": nav_routes},
        )
    else:
        nav_routes = navigator.process_route(nav_routes)
        logger.warning(nav_routes)
        geojson = [
            {
                "type": "Feature",
                "properties": {
                    "route_id": route[0],
                    "start_milepost": route[1],
                    "end_milepost": route[2],
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": navigator.get_geometry([route]),
                },
            }
            for route in nav_routes
        ]
        return {"type": "FeatureCollection", "features": geojson}
