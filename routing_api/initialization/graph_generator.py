import networkx as nx
import json

routes = json.load(open("routing_api/routes_with_mile_markers.json"))
intersections = json.load(open("routing_api/intersection_data_array.json"))


def get_node_id(route_id, milepost):
    return f"{route_id}-{milepost:.2f}"


def handle_new_node(G: nx.Graph, route_id, milepost):

    # 1. check if node exists in graph
    # 2. if node exists, return node id
    # 3. if node does not exist (assume we are placing in the middle of another edge):
    #   a. create a new node
    #   b. find the edge that contains the milepost
    #   c. remove the edge
    #   d. add two new edges, one from start to milepost and one from milepost to end
    #   e. return the new node id

    node_id = get_node_id(route_id, milepost)
    if node_id in G.nodes:
        return node_id
    G.add_node(node_id, route=route_id, mm=milepost)
    edge = None
    for e in G.edges:
        if e[0].split("-")[0] == route_id and e[1].split("-")[0] == route_id:
            if float(e[0].split("-")[1]) <= milepost <= float(
                e[1].split("-")[1]
            ) or float(e[1].split("-")[1]) <= milepost <= float(e[0].split("-")[1]):
                edge = e
                break
    if not edge:
        print(f"Error: Could not find edge for {route_id} and {milepost}")
        return None
    # edge found. remove edge, connect start and end to new node
    G.remove_edge(edge[0], edge[1])
    G.add_edge(edge[0], node_id, distance=abs(milepost - float(edge[0].split("-")[1])))
    G.add_edge(node_id, edge[1], distance=abs(float(edge[1].split("-")[1]) - milepost))


# def insert_edge_into_center(G: nx.Graph, route_id, edge, milepost, edges):
#     # find edge in route_1['edges'] that contains milepost_1
#     G.remove_edge(get_node_id(route_id, edge[0]), get_node_id(route_id, edge[1]))
#     edges.remove(edge)
#     G.add_edge(get_node_id(route_id, edge[0]), node_id, distance=milepost - edge[0])
#     G.add_edge(node_id, get_node_id(route_id, edge[1]), distance=edge[1] - milepost)
#     edges.append((edge[0], milepost))
#     edges.append((milepost, edge[1]))


# Initialize graph
G = nx.Graph()

keyed_routes = {}
nodes = {}
for route in routes:
    if not route["Geometry"]:
        continue
    keyed_routes[route["Route"]] = route
    G.add_node(
        get_node_id(route["Route"], route["MMin"]),
        route=route["Route"],
        mm=route["MMin"],
    )
    G.add_node(
        get_node_id(route["Route"], route["MMax"]),
        route=route["Route"],
        mm=route["MMax"],
    )
    G.add_edge(
        get_node_id(route["Route"], route["MMin"]),
        get_node_id(route["Route"], route["MMax"]),
        distance=route["MMax"] - route["MMin"],
    )
    keyed_routes[route["Route"]]["nodes"] = [route["MMin"], route["MMax"]]
    keyed_routes[route["Route"]]["edges"] = [(route["MMin"], route["MMax"])]

for intersection in intersections:
    route_id_1 = intersection["route_id_1"]
    route_id_2 = intersection["route_id_2"]
    milepost_1 = intersection["milepost_1"]
    milepost_2 = intersection["milepost_2"]

    route_1 = keyed_routes[route_id_1]
    route_2 = keyed_routes[route_id_2]

    node_1_id = handle_new_node(G, route_id_1, milepost_1)
    node_2_id = handle_new_node(G, route_id_2, milepost_2)
    if not node_1_id or not node_2_id:
        continue
    # Assumption: nodes are coincident
    G.add_edge(node_1_id, node_2_id, distance=0)


# Graph is now set up with routes as nodes and intersections as edges
print("Graph nodes:", list(G.nodes(data=True)))
print("Graph edges:", list(G.edges(data=True)))

# # Save the graph in a binary format (e.g., for easy reloading within Python)
nx.write_gml(G, "routing_api/route_graph.gml")

# Alternatively, save in GraphML format (for use in other tools)
# nx.write_graphml(G, "routing_api/route_graph.graphml")

# You can load the gpickle file later using:
# G = nx.read_gpickle("routing_api/route_graph.gpickle")
# G = nx.read_graphml("routing_api/route_graph.graphml")

print("Graph saved successfully.")
