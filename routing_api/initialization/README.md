# Geospatial API Routing

This project pulls in route geometry, detects intersections, generates a graph, and enables navigation between different routes. The scripts are as follows:

- route_generator.py: Pull geometry for all routes from the geospatial api. Create the following files:
  - routes.json: array of all routes with id and mileposts
  - routes_with_geometry.json: array of all routes with Geometry: list<list<long,lat>>
  - _unused - routes_with_intersections.json: array of naive end-to-end intersections_
  - _unused - routes_with_intersections_no_geometry.json: array of routes with intersections tagged on_
  - routes.geojson: all routes in geojson format
  - _unused - intersection_points.geojson: naive intersections as points_
- intersection_generator.py: use geopandas to detect geometrically intersecting routes
  - input: routes_with_geometry.json
  - routes_with_mile_markers.json: routes with estimated mile markers for each geometry point
  - intersection_data_array.json: array of detected intersection points, with route ids and mileposts
- graph_generator.py: compile routes and intersections into a networkx graph
  - input: routes_with_mile_markers.json
  - input: intersection_data_array.json
  - route_graph.gml: compiled graph. Nodes are "{route_id}-{milepost}", and edges span nodes with the property distance, in miles. Intersections are connected by nodes with distance=0
- navigator.py: use graph to generate paths between two arbitrary route id/milepost pairs
  - input: route_graph.gml
  - spits out a processed route, like [('040C', 300.0, 279.21), ('121A', 17.08, 20.0)]
  - This navigation follows a few rules:
    - method: shortest distance
    - post-process: remove intermediate nodes with no route change
    - post-process: remove intermediate nodes which leave and return to the same route
    - collect route ids and milepost ranges as output
