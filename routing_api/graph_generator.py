import networkx as nx
import json

routes = json.load(open("routing_api/routes_with_mile_markers.json"))
intersections = json.load(open("routing_api/intersection_data_array.json"))

# Initialize graph
G = nx.Graph()

# Add route data as nodes, including MMin and MMax points
for route in routes:
    if not route["Geometry"]:
        continue
    route_id = route["Route"]
    mileposts = route["Distances"]
    geometry = route["Geometry"]

    # Get MMin and MMax
    mmin = route["MMin"]
    mmax = route["MMax"]

    # Add nodes for each milepost (and intersections)
    for milepost in mileposts:
        node_id = f"{route_id}_{milepost}"

        # Find the closest geometry point for this milepost
        geometry_index = min(
            range(len(mileposts)), key=lambda i: abs(mileposts[i] - milepost)
        )
        coordinates = geometry[geometry_index]

        # Add node to the graph if it doesn’t exist
        if node_id not in G:
            G.add_node(
                node_id, route_id=route_id, milepost=milepost, coordinates=coordinates
            )

    # Add MMin node if it’s not already an intersection
    mmin_node_id = f"{route_id}_{mmin}"
    if mmin_node_id not in G:
        mmin_coordinates = geometry[
            0
        ]  # Assuming first point in geometry represents MMin
        G.add_node(
            mmin_node_id, route_id=route_id, milepost=mmin, coordinates=mmin_coordinates
        )
        # Connect MMin to the first milepost or intersection
        first_milepost_node = f"{route_id}_{mileposts[0]}"
        G.add_edge(mmin_node_id, first_milepost_node)

    # Add MMax node if it’s not already an intersection
    mmax_node_id = f"{route_id}_{mmax}"
    if mmax_node_id not in G:
        mmax_coordinates = geometry[
            -1
        ]  # Assuming last point in geometry represents MMax
        G.add_node(
            mmax_node_id, route_id=route_id, milepost=mmax, coordinates=mmax_coordinates
        )
        # Connect MMax to the last milepost or intersection
        last_milepost_node = f"{route_id}_{mileposts[-1]}"
        G.add_edge(last_milepost_node, mmax_node_id)

# Add intersections as edges
for intersection in intersections:
    route_id_1 = intersection["route_id_1"]
    route_id_2 = intersection["route_id_2"]
    milepost_1 = intersection["milepost_1"]
    milepost_2 = intersection["milepost_2"]
    coordinates = tuple(intersection["coordinates"])

    # Define node ids for the intersection points on each route
    node_id_1 = f"{route_id_1}_{milepost_1}"
    node_id_2 = f"{route_id_2}_{milepost_2}"

    # Add nodes if they aren't already present
    if node_id_1 not in G:
        G.add_node(
            node_id_1, route_id=route_id_1, milepost=milepost_1, coordinates=coordinates
        )
    if node_id_2 not in G:
        G.add_node(
            node_id_2, route_id=route_id_2, milepost=milepost_2, coordinates=coordinates
        )

    # Add edge between the two intersecting nodes
    G.add_edge(node_id_1, node_id_2, intersection_coordinates=coordinates)

# Graph is now set up with routes as nodes and intersections as edges
print("Graph nodes:", list(G.nodes(data=True)))
print("Graph edges:", list(G.edges(data=True)))

# # Save the graph in a binary format (e.g., for easy reloading within Python)
nx.write_gpickle(G, "routing_api/route_graph.gpickle")

# Alternatively, save in GraphML format (for use in other tools)
# nx.write_graphml(G, "routing_api/route_graph.graphml")

# You can load the gpickle file later using:
# G = nx.read_gpickle("routing_api/route_graph.gpickle")
# G = nx.read_graphml("routing_api/route_graph.graphml")

print("Graph saved successfully.")
