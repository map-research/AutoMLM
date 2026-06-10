"""
Provides structure for precedence graphs, required for property-precedence analysis.
The precedence graph is a directed graph, with the direction a -> b expressing reverse precedence (i.e., b < a)
This allows interpreting the topological order of the graph as instantiation levels.
"""
import os.path
from graphlib import TopologicalSorter
import pydot

from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute


class PrecedenceGraph:
    def __init__(self):
        self.nodes: {} = {}
        self.edges: [] = []
        self.pydot_graph = None

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
            case "=" | "?":
                "s"  # ignore for now
            case _:
                raise ValueError(f"Unrecognized attribute relation: {rel_symbol}. Precedence graph couldn't be updated")

    def get_static_order(self) -> ():
        top_sorter: TopologicalSorter = TopologicalSorter(self.nodes)
        return tuple(top_sorter.static_order())

    def export_graph_as_png(self, graph_name: str):
        if self.pydot_graph is None:
            self.create_pydot_graph()
        self.pydot_graph.write_png(os.path.join("test_file_outputs", f"{graph_name}_PropertyPrecedenceGraph.png"))

    def export_graph_as_svg(self, graph_name: str):
        if self.pydot_graph is None:
            self.create_pydot_graph()
        self.pydot_graph.write_png(os.path.join("test_file_outputs", f"{graph_name}_PropertyPrecedenceGraph.svg"))

    def create_pydot_graph(self):
        self.pydot_graph = pydot.Dot("Proper Precedence Graph", graph_type='digraph')
        for node in self.nodes.keys():
            self.pydot_graph.add_node(pydot.Node(node.attr_name))
        for edge in self.edges:
            self.pydot_graph.add_edge(pydot.Edge(edge[0].attr_name, edge[1].attr_name))

    def plot_precedence_graph(self):
        self.pydot_graph().create_svg()

    def __repr__(self):
        return f"[PRECEDENCE GRAPH]({self.nodes}"
