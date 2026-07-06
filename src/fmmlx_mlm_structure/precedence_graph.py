"""
Provides structure for precedence graphs, required for property-precedence analysis.
The precedence graph is a directed graph, with the direction a -> b expressing reverse precedence (i.e., b < a)
This allows interpreting the topological order of the graph as instantiation levels.
"""
import datetime
import itertools
import os.path
from graphlib import TopologicalSorter
from typing import Any, Iterable

import networkx as nx
import pydot
from networkx import DiGraph

from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.model_property import ModelProperty
from src.fmmlx_mlm_structure.model_property_enum import ModelPropertyEnum
from src.fmmlx_mlm_structure.property_group import PropertyGroup


class PropertyPrecedenceGraph:
    """Property precedence graph used for property precedence analysis. The graph is implemented through an
    adjacency list via a dictionary. Additionally, a redundant list containing all edges is maintained.
    This is done in order to simplify the generation of graph images."""

    def __init__(self):
        self.nodes: {} = {}
        self.edges: [] = []
        self.poly_property_groups: [PropertyGroup] = []  # used for quicker checks, items should be
        # property groups with at least 2 model properties
        self.pydot_graph = None
        self.nx_digraph: DiGraph = None
        self.property_type: ModelPropertyEnum = ModelPropertyEnum.UNDEFINED
        self.output_folder: str = "test_file_outputs"  # default folder used for generated images

    def _add_property_precedence_to_graph(self, pg1: PropertyGroup, pg2: PropertyGroup):
        """All property groups received as input here should only include one model property"""
        assert len(pg1) == 1 and len(pg2) == 1, "Property groups, at this stage, must only include one model property"
        for poly_pg in self.poly_property_groups:
            if poly_pg.includes_model_property(pg1.get_model_properties()[0]):
                pg1 = poly_pg
                # if pg1 is already part of a shared pg, then the precedence may be duplicate
                if pg1 in self.nodes.keys():
                    if pg2 in self.nodes[pg1]:
                        return
            if poly_pg.includes_model_property(pg2.get_model_properties()[0]):
                # if pg2 is already part of a shared pg, the precedence must have been added already
                pg2 = poly_pg
                return
        #  print(f"->To Graph we add: {pg1} precedes {pg2}")
        if pg1 in self.nodes:
            current_connections: [] = self.nodes.get(pg1)
            current_connections.append(pg2)
            self.nodes.update({pg1: current_connections})
        else:
            self.nodes.update({pg1: [pg2]})
        if pg2 not in self.nodes:
            #  pg2 is also added as a node to the adjacency list so that every node can be accessed by traversing the
            # keys of the self.nodes dict
            self.nodes.update({pg2: []})
        self.edges.append((pg1, pg2))

    def _update_property_group(self, key, old_pg_groups: [PropertyGroup], new_p_group: PropertyGroup):
        """This function is primarily used in order to update connected nodes kept in value lists of the self.nodes
        dictionary. The update shall aggregate property groups as required."""
        connections: [] = self.nodes.get(key)
        pg_updated: bool = False
        for pg in connections:
            if pg in old_pg_groups:
                # TODO IMPORTANT!
                # old_pg_groups may contain pgs with multiple properties,
                # causing an error in the implemented equality operator
                self.nodes[key].remove(pg) # note that 'remove' exits after first occurrence, but shouldn't be a problem
                if not pg_updated:
                    connections.append(new_p_group)
                    pg_updated = True

    def _update_shared_property_group(self, pg1: PropertyGroup, pg2: PropertyGroup):
        """This operation is called when two property groups are detected to be concormitant and should thus be
        part of a shared property group. In this case (i) all existing keys containing either pg must be updated to
        the shared pg and (ii) all values containing either pg must be updated to the shared pg.

        The property groups received here as inputs are always single-property groups. Thus, it must be checked whether
        the contained properties are already part of other poly-property groups.
        """
        found_pg1_key: bool = False
        found_pg2_key: bool = False
        pg1_in_poly_pg: bool = False
        pg2_in_poly_pg: bool = False
        shared_prop_group: PropertyGroup = PropertyGroup()
        shared_prop_group.merge_other_property_groups(pg1, pg2)
        prop_connections: [] = []  # used to update keys

        #  Step1 : check for poly-property groups
        for poly_pg in self.poly_property_groups:
            poly_pg_properties = poly_pg.get_model_properties()
            pg1_in_poly_pg = False
            pg2_in_poly_pg = False
            if pg1.get_model_properties() in poly_pg:
                pg1_in_poly_pg = True
            if pg2.get_model_properties() in poly_pg:
                pg2_in_poly_pg = True
            if pg1_in_poly_pg or pg2_in_poly_pg:
                shared_prop_group: PropertyGroup = PropertyGroup()
                if pg1_in_poly_pg:
                    shared_prop_group.merge_other_property_groups(poly_pg, pg2)
                if pg2_in_poly_pg:
                    shared_prop_group.merge_other_property_groups(poly_pg, pg1)
                if pg1_in_poly_pg and pg2_in_poly_pg:
                    shared_prop_group.merge_other_property_groups(poly_pg)

        #  Step 2: check nodes
        for key in self.nodes:
            if key == pg1:
                found_pg1_key = True
            if key == pg2:
                found_pg2_key = True
        if found_pg1_key or found_pg2_key:
            if found_pg1_key:
                prop_connections.append(self.nodes[pg1])
                self.nodes.pop(pg1)
            if found_pg2_key:
                prop_connections.append(self.nodes[pg2])
                self.nodes.pop(pg2)
            if prop_connections == [[]]:  # this odd case occurs when an empty node is being updated.
                # it must be prevented here in order to avoid type error elsewhere
                prop_connections = []
            #  print(f"SHARED UPGRADE {shared_prop_group}: {prop_connections}")
            self.nodes.update({shared_prop_group: prop_connections})

        #  Step 3: check values
        # HERE: regardless of whether they have already been keys, all values mentioning either p1 or p2 must be updated
        self.poly_property_groups.append(shared_prop_group)
        for key, values in self.nodes.items():
            if pg1 in values or pg2 in values:
                self._update_property_group(key=key, old_pg_groups=[pg1, pg2], new_p_group=shared_prop_group)
        self._update_shared_property_group_for_edges(pg1, pg2, shared_prop_group)

    def _update_shared_property_group_for_edges(self, pg1: PropertyGroup, pg2: PropertyGroup, shared_pg: PropertyGroup):
        """This is a surrogate function to _update_shared_property_group. It is required to keep the edges list in sync
        with the dictionary"""
        new_edge: () = ()  # tuples are immutable, if edge must be updated, new tuple is required
        updated_edge: bool = False
        for edge_index, edge in enumerate(self.edges):
            new_edge = ()
            updated_edge = False
            if edge[0] == pg1 or edge[0] == pg2:
                new_edge = (shared_pg, edge[1])
                updated_edge = True
            if edge[1] == pg1 or edge[1] == pg2:
                new_edge = (edge[0], shared_pg)
                updated_edge = True
            if updated_edge:
                self.edges[edge_index] = new_edge

    def add_property_relation(self, prop1: ModelProperty, prop2: ModelProperty, rel_symbol: str):
        pg1: PropertyGroup = PropertyGroup(prop1)
        pg2: PropertyGroup = PropertyGroup(prop2)
        #  print(f"We add the following: {pg1} {rel_symbol} {pg2}")
        # This always creates new property groups even if identical in content!!!
        # Thus, changed equality operator for model properties
        match rel_symbol:
            case "<" | "<=":
                self._add_property_precedence_to_graph(pg1, pg2)
            case ">" | ">=":
                self._add_property_precedence_to_graph(pg2, pg1)
            case "=":
                self._update_shared_property_group(pg1, pg2)
            case "?":
                return  # ignore for now
            case "||":
                return # disjoint sets, can be ignored
            case _:
                raise ValueError(f"Unrecognized attribute relation: {rel_symbol}. Precedence graph couldn't be updated")

    def get_static_order(self) -> ():
        top_sorter: TopologicalSorter = TopologicalSorter(self.nodes)
        return tuple(top_sorter.static_order())

    def init_nx_graph(self):
        if self.nx_digraph is None:
            self.nx_digraph = nx.DiGraph(self.edges)

    def get_topological_generations(self) -> []:
        self.init_nx_graph()
        return [sorted(generation) for generation in nx.topological_generations(self.nx_digraph)]

    def export_graph_as_png(self, graph_name: str):
        if self.pydot_graph is None:
            self.create_pydot_graph()
        self.pydot_graph.write_png(os.path.join(self.output_folder, self._get_image_file_name(graph_name, "png")))

    def export_graph_as_svg(self, graph_name: str):
        if self.pydot_graph is None:
            self.create_pydot_graph()
        self.pydot_graph.write_svg(os.path.join(self.output_folder, self._get_image_file_name(graph_name, "svg")))

    def _get_image_file_name(self, graph_name: str, format: str) -> str:
        today = datetime.datetime.now()
        time_str: str = f"{today.year}{today.month}{today.day}"
        suffix: int = 1
        filename: str = f"{graph_name}_{self.property_type.value}PrecedenceGraph_v{time_str}-v{str(suffix)}.{format}"
        while os.path.exists(os.path.join(self.output_folder, filename)):
            suffix += 1
            filename = f"{graph_name}_{self.property_type.value}PrecedenceGraph_v{time_str}-v{str(suffix)}.{format}"
        return filename

    def create_pydot_graph(self):
        self.pydot_graph = pydot.Dot("Precedence Graph", graph_type='digraph')
        self._transitive_reduction()
        for pg_node in self.nodes.keys():
            self.pydot_graph.add_node(pydot.Node(pg_node.get_print_name()))
            #  print(f"PYDOT added NODE: {pg_node.get_print_name()}")
        for edge in self.edges:
            self.pydot_graph.add_edge(pydot.Edge(edge[0].get_print_name(), edge[1].get_print_name()))
            #  print(f"PYDOT added EDGE: {edge[0].get_print_name()} TO {edge[1].get_print_name()}")

    def _remove_edge(self, mp1: ModelProperty, mp2: ModelProperty):
        """This helper function only removes edges from the redundant edges list. This is done to support
        transitive reduction of PyDot Graphs, which visualize the edges in this list"""
        edge = (mp1, mp2)
        try:
            self.edges.remove(edge)
        except:
            print(f"FAILED TO REMOVE EDGE {(mp1, mp2)}")

    def _transitive_reduction(self):
        """Transitive reduction algorithm used only for edges list and thus only concerns graph visualization"""
        for x in self.nodes.keys():
            for y in self.nodes.keys():
                for z in self.nodes.keys():
                    if (x, y) in self.edges and (y, z) in self.edges and (x, z) in self.edges:
                        self._remove_edge(x, z)

    def __repr__(self):
        rs: str = f"[{self.property_type.value.upper()} PRECEDENCE GRAPH]\n"
        for node, conns in self.nodes.items():
            rs += f"\t{node}: {conns}\n"
        return rs

    def return_edges_for_print(self):
        rs: str = "[PRECEDENCE GRAPH EDGES]\n"
        for edge in self.edges:
            rs += f"\tEdge From {edge[0]} to {edge[1]}\n"
        return rs
