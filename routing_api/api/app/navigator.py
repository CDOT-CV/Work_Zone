from typing import List, Tuple
import networkx as nx


def extract_milepost_from_node(node_id: str) -> float:
    """Extract the milepost from a node ID"""
    return float(node_id.split("-")[1])


def add_temporary_node(G: nx.Graph, route_id: str, milepost: float, temp_node_id: str):
    # Identify edges on this route in the graph
    route_edges = [
        (u, v, d) for u, v, d in G.edges(data=True) if route_id in u and route_id in v
    ]

    if not route_edges:
        print(f"Error: Could not find edges for {route_id}")
        return None

    # Find the edge closest to the desired milepost
    closest_edge = min(
        route_edges,
        key=lambda edge: abs(extract_milepost_from_node(edge[0]) - milepost)
        + abs(extract_milepost_from_node(edge[1]) - milepost),
    )
    u, v, data = closest_edge

    # Calculate distances for splitting
    u_milepost = extract_milepost_from_node(u)
    v_milepost = extract_milepost_from_node(v)
    dist_to_u = abs(milepost - u_milepost)
    dist_to_v = abs(milepost - v_milepost)

    # Remove the original edge and add the temporary node with new edges
    G.remove_edge(u, v)
    G.add_node(temp_node_id, route=route_id, milepost=milepost)
    G.add_edge(u, temp_node_id, distance=dist_to_u)
    G.add_edge(temp_node_id, v, distance=dist_to_v)
    return True


# def remove_temporary_node(G: nx.Graph, temp_node_id: str):
#     # Identify the edges connected to the temporary node
#     edges = list(G.edges(temp_node_id, data=True))

#     # Get the nodes at the ends of the edges
#     u = edges[0][0]
#     v = edges[0][1]

#     # Calculate the distance between the nodes
#     distance = edges[0][2]["distance"] + edges[1][2]["distance"]

#     # Remove the temporary node and add the edge between the original nodes
#     G.remove_node(temp_node_id)
#     G.add_edge(u, v, distance=distance)


def get_navigation_route(
    G: nx.Graph, start_rid: str, start_mm: float, end_rid: str, end_mm: float
) -> nx.Graph:
    """Get the shortest path between two mileposts on different routes"""

    if start_rid == end_rid:
        return [f"{start_rid}-{start_mm}", f"{end_rid}-{end_mm}"]

    # Create temporary nodes
    temp_node_1 = f"{start_rid}-{start_mm}"
    temp_node_2 = f"{end_rid}-{end_mm}"

    # Add temporary nodes to the graph
    if not add_temporary_node(G, start_rid, start_mm, temp_node_1):
        return []
    if not add_temporary_node(G, end_rid, end_mm, temp_node_2):
        return []

    # Find the shortest path
    shortest_path = nx.shortest_path(G, temp_node_1, temp_node_2, weight="distance")

    # # Remove temporary nodes from the graph
    # remove_temporary_node(G, temp_node_1)
    # remove_temporary_node(G, temp_node_2)

    return shortest_path


def process_route(route: List[str]) -> Tuple[str, float]:
    # create a list of route IDs and mile marker ranges of the route
    # remove unnecessary route changes
    #    if route id doesn't change, remove
    #    if route id changes and comes back eventually, remove the intermediate route changes

    path = []
    for route_name in route:
        route_id = route_name.split("-")[0]
        mm = float(route_name.split("-")[1])
        if not path or len(path) <= 2:
            path.append((route_id, mm))
            continue
        if route_id != path[-1][0]:
            if route_id in [x[0] for x in path]:
                # remove the intermediate route changes
                i = [x[0] for x in path].index(route_id) + 1
                path = path[:i]
        path.append((route_id, mm))

    # collect route paths together
    transfers = []
    for i in range(len(path)):
        if not transfers or path[i][0] != transfers[-1][0]:
            transfers.append((path[i][0], path[i][1], path[i][1]))
        else:
            transfers[-1] = (transfers[-1][0], transfers[-1][1], path[i][1])
    return transfers
