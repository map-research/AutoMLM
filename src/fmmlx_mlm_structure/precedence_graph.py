"""
Provides structure for precedence graphs, required for property-precedence analysis.
The precedence graph is a directed graph, with the direction a -> b expressing reverse precedence (i.e., b < a)
This allows interpreting the topological order of the graph as instantiation levels.
"""
from graphlib import TopologicalSorter
from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute


class PrecedenceGraph:
    def __init__(self):
        self.nodes: {} = {}
        self.edges: [] = []

    def add_node_connection(self, node1: FmmlxAttribute, node2: FmmlxAttribute):
        if node1 in self.nodes:
            current_connections: [FmmlxAttribute] = self.nodes.get(node1)
            current_connections.append(node2)
            self.nodes.update({node1: current_connections})
        else:
            self.nodes.update({node1: [node2]})
        self.edges.append((node1, node2))

    def add_attribute_relation(self, attr1: FmmlxAttribute, attr2: FmmlxAttribute, rel_symbol: str):
        match rel_symbol:
            case "<" | "<=":
                self.add_node_connection(attr1, attr2)
            case ">" | ">=":
                self.add_node_connection(attr2, attr1)
            case "=":
                "s"
            case _:
                raise ValueError(f"Unrecognized attribute relation: {rel_symbol}. Precedence graph couldn't be updated")

    def get_static_order(self) -> ():
        top_sorter: TopologicalSorter = TopologicalSorter(self.nodes)
        return tuple(top_sorter.static_order())

    def __repr__(self):
        return f"[PRECEDENCE GRAPH]({self.nodes}"
