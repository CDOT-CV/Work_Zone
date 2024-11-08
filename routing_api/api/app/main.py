import datetime

from fastapi import FastAPI, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from models import (
    Route,
    RouteWithGeometry,
    PathRoutingRequest,
    NavigationPathSegment,
)

import navigator

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


##################################################################
# Rest Endpoint
##################################################################
@app.get("/")
def read_root():
    logger.debug(
        f"Received request to / at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    return f"CDOT Graph Routing API, Version {API_VERSION}"


@app.get("/routes", description="Return a list of all available environments, by name")
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


@app.post("/path", description="Return a list of all available environments, by name")
async def get_path(
    path_request: PathRoutingRequest,
) -> list[NavigationPathSegment]:
    logger.debug(
        f"Received request to /path at {datetime.datetime.now(pytz.utc).strftime(ISO_8601_FORMAT_STRING)}"
    )
    RouteGraphyCopy = RouteGraph.copy()
    routes = navigator.get_navigation_route(
        RouteGraphyCopy,
        path_request.from_route_id,
        path_request.from_milepost,
        path_request.to_route_id,
        path_request.to_milepost,
    )
    if not routes:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"Error": "Route(s) not found"},
        )
    else:
        path_segments = [
            NavigationPathSegment(
                route_id=route[0], start_milepost=route[1], end_milepost=route[2]
            )
            for route in navigator.process_route(routes)
        ]
        logger.warning(path_segments)
        return path_segments
