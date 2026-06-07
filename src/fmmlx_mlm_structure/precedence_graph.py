"""
Provides structure for precedence graphs, required for property-precedence analysis
"""


class PrecedenceGraph:
    def __init__(self):
        self.nodes: {} = {}
        self.edges: [] = []

    def add_node(self, node: str):
        assert node not in self.nodes, "Node (name) already exists"
        self.nodes.update({node: ""})

    def add_directed_node_connection(self, node1: str, node2: str):
        assert node1 in self.nodes, f"Node ({node1}) not found in precedence graph"
        
