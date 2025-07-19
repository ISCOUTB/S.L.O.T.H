# TODO: Search for another way to count the number of connections, because
# the current one, could be very inefficient for large graphs.
from igraph import Graph


def get_outgoing_connections(graph: Graph, source_node: str) -> int:
    """
    Returns the number of outgoing connections from the specified node
    from the adjacency matrix.

    Args:
        graph (Graph): The igraph Graph object.
        source_node (str): The name of the node to check.

    Returns:
        int: The number of outgoing connections from the specified node.
    """
    vertex_names = graph.vs["name"]
    adjacency = graph.get_adjacency()
    i = vertex_names.index(source_node) if source_node in vertex_names else -1
    if i == -1 or i >= len(adjacency):
        return 0

    return sum(adjacency[i])


def get_incoming_connections(graph: Graph, target_node: str) -> int:
    """
    Returns the number of incoming connections to the specified node
    from the adjacency matrix.

    Args:
        graph (Graph): The igraph Graph object.
        target_node (str): The name of the node to check.

    Returns:
        int: The number of incoming connections to the specified node.
    """
    vertex_names = graph.vs["name"]
    adjacency = graph.get_adjacency()
    i = vertex_names.index(target_node) if target_node in vertex_names else -1
    if i == -1 or i >= len(adjacency):
        return 0

    return sum(list(map(lambda row: row[i], adjacency)))


def has_cyclic_dependencies(graph: Graph) -> bool:
    """
    Checks if the graph has cyclic dependencies.

    Args:
        graph (Graph): The igraph Graph object.

    Returns:
        bool: True if the graph has cyclic dependencies, False otherwise.
    """
    return not graph.is_dag()  # Directed Acyclic Graph check


def get_priority_level(graph: Graph, source_node: str) -> int:
    """Calculate the priority level of a node in a directed graph.

    The priority level represents the depth of the longest path from the given
    source node to any leaf node in the graph. A leaf node (with no outgoing
    edges) has a priority level of 0, and each parent node's priority level
    is 1 plus the maximum priority level of its children.

    Args:
        graph (Graph): An igraph Graph object containing the directed graph.
        source_node (str): The name of the source node to calculate priority for.

    Returns:
        int: The priority level of the source node. Returns 0 if the node
             doesn't exist in the graph, is out of bounds, or has no outgoing
             edges.
    """
    if has_cyclic_dependencies(graph):
        raise ValueError(
            "The graph is not a directed acyclic graph (DAG). This function "
            "is only designed for DAGs."
        )

    vertex_names = graph.vs["name"]
    adjacency = graph.get_adjacency()
    i = vertex_names.index(source_node) if source_node in vertex_names else -1

    # If i is out of boundes
    if i == -1 or i >= len(adjacency):
        return 0

    if sum(adjacency[i]) == 0:
        return 0

    return sum(
        1 + get_priority_level(graph, vertex_names[j])
        for j in range(len(adjacency))
        if adjacency[i][j] > 0
    )
