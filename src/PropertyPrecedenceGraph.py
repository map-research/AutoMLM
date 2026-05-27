from enum import Enum
from itertools import chain

from src.mlm_helper_classes import *


class InstLevelOrder(Enum):
    HIGHER = ">"
    SAME = "="
    LOWER = "<"
    UNDEFINED = "?"


class PropertyPrecedenceGraph(object):
    def __init__(self, attribute_value_lists):
        self.precedence_graph = {}
        self.attribute_value_lists = attribute_value_lists
        self._initialize_graph()

    def _initialize_graph(self):
        all_attribute_labels = [attr_value_list[0].attr_name for attr_value_list in self.attribute_value_lists]

        for current_attr_iter in range(len(all_attribute_labels)):
            current_attr = all_attribute_labels[current_attr_iter]
            self.precedence_graph.update({current_attr: []})
            dependency_relationships_for_node = []
            for next_attr_iter in range(current_attr_iter+1,len(all_attribute_labels)):
                next_attr = all_attribute_labels[next_attr_iter]
                dependency_rel: DependencyRelationship = (
                    DependencyRelationship(current_attr, next_attr,
                                           self.attribute_value_lists[current_attr_iter][1],
                                           self.attribute_value_lists[next_attr_iter][1]))
                dependency_relationships_for_node.append(dependency_rel)
            if current_attr_iter > 0:
                for current_dependency in list(chain.from_iterable(self.precedence_graph.values())):
                    if current_dependency.contains(prop=current_attr):
                        dependency_relationships_for_node.append(current_dependency)
                        self.precedence_graph.update({current_attr: dependency_relationships_for_node})
            else:
                self.precedence_graph.update({current_attr: dependency_relationships_for_node})

    def get_all_dependency_relationships(self):
        return list(chain.from_iterable(self.precedence_graph.values()))

    def perform_multiplicity_analysis(self):
        rel_encountered = []
        for dependency_rel in self.get_all_dependency_relationships():
            if dependency_rel not in rel_encountered:
                dependency_rel.value_mapping_analysis()
                rel_encountered.append(dependency_rel)

    def get_conflict_free_attributes(self):
        all_conflict_free_attr = []
        for attr_name in self.precedence_graph:
            if self._is_attr_conflict_free(attr_name):
                all_conflict_free_attr.append(attr_name)
        return all_conflict_free_attr

    def get_reordered_mlm_attributes(self) -> [MlmAttr]:
        break_counter = 0
        attr_list = []
        while len(self.get_conflict_free_attributes())>0:
            inst_level = break_counter
            lowest_attr = self.get_lowest_attributes()
            if len(lowest_attr)==0:
                lowest_attr = list(self.precedence_graph.keys())
            for attr in lowest_attr:
                new_attr: MlmAttr = MlmAttr(attr, "Root::XCore::String", inst_level)
                attr_list.append(new_attr)
            break_counter += 1
            if break_counter > 5:
                break
            for cf_attr in lowest_attr:
                self.remove_attr_from_graph(cf_attr)
        return attr_list


    def get_lowest_attributes(self):
        conflict_free_attrs = self.get_conflict_free_attributes()
        lowest_attrs = []
        for conflict_free_attr in conflict_free_attrs:
            may_be_lowest: bool = True
            all_edges = self.precedence_graph.get(conflict_free_attr)
            for edge in all_edges:
                if edge.property_a == conflict_free_attr:
                    if not edge.get_lower_or_equals():
                        may_be_lowest = False
                if edge.property_b == conflict_free_attr:
                    if not edge.get_higher_or_equals():
                        may_be_lowest = False
            if may_be_lowest:
                lowest_attrs.append(conflict_free_attr)
        return lowest_attrs

    def remove_attr_from_graph(self, attr_name: str):
        self.precedence_graph.pop(attr_name)
        for attr in self.precedence_graph:
            all_edges = self.precedence_graph.get(attr)
            for edge_iter in range(len(all_edges)):
                edge = all_edges[edge_iter]
                if edge.contains(attr_name):
                    all_edges.pop(edge_iter)
                    break
            self.precedence_graph.update({attr: all_edges})



    def _is_attr_conflict_free(self, attr_name: str):
        dependency_relationships = self.precedence_graph[attr_name]
        for dep_rel in dependency_relationships:
            if dep_rel.inst_level_order == InstLevelOrder.UNDEFINED:
                return False
        return True
    def _get_slot_values_for_attr_label(self, attr_label: str):
        for attribute_value_list in self.attribute_value_lists:
            if attribute_value_list[0].attr_name == attr_label:
                return attribute_value_list[1]
        return []

    def get_dependency_relationships_for_node(self, node:str):
        if node in self.precedence_graph:
            return self.precedence_graph.get(node)

    def get_all_properties(self):
        return self.precedence_graph.keys()

    # returns graph items as list of tuples
    def get_items(self):
        return self.precedence_graph.items()

    def __repr__(self):
        return str(self.precedence_graph)

# Class Property is Node
class Node(object):
    def __init__(self, label: str, value_array=None):
        if value_array is None:
            value_array = []
        self.label = label
        self.value_array = value_array


class MultiplicityEnum(Enum):
    UNBOUND = "*"
    ONE = "1"
    NONE = "XXX"

# Dependency Relationship is Edge
class DependencyRelationship(object):
    def __init__(self, property_a: str, property_b: str, set_of_values_a, set_of_values_b):
        self.property_a = property_a
        self.property_b = property_b
        self.set_of_values_a = set_of_values_a
        self.set_of_values_b = set_of_values_b
        self.dominance_weight_a: float = 1
        self.dominance_weight_b: float = 1
        self.multiplicity_a: MultiplicityEnum = MultiplicityEnum.ONE
        self.multiplicity_b: MultiplicityEnum = MultiplicityEnum.ONE
        self.dependency_values_a = (self.multiplicity_a, self.dominance_weight_a)
        self.dependency_values_b = (self.multiplicity_b, self.dominance_weight_b)
        self.inst_level_order: InstLevelOrder = InstLevelOrder.UNDEFINED

    def contains(self, prop: str):
        if self.property_a == prop or self.property_b == prop:
            return True
        else:
            return False

    def set_multiplicity_a(self, multiplicity_a: MultiplicityEnum):
        self.multiplicity_a = multiplicity_a

    def set_multiplicity_b(self, multiplicity_b: MultiplicityEnum):
        self.multiplicity_b = multiplicity_b

    def set_dominance_weight_a(self, dominance_weight_a: float):
        self.dominance_weight_a = dominance_weight_a

    def set_dominance_weight_b(self, dominance_weight_b: float):
        self.dominance_weight_b = dominance_weight_b

    def value_mapping_analysis(self):
        zipped_values = tuple(zip(self.set_of_values_a,self.set_of_values_b))
        encountered_a = []
        encountered_b = []
        for current_value_a, current_value_b in zipped_values:
            current_value_a = current_value_a.lower()
            current_value_b = current_value_b.lower()
            len_of_encountered_values = len(encountered_a)
            if len_of_encountered_values > 0:
                for past_value_iter in range(len_of_encountered_values):
                    past_value_a = encountered_a[past_value_iter].lower()
                    past_value_b = encountered_b[past_value_iter].lower()
                    if current_value_a == past_value_a:
                        if current_value_b != past_value_b:
                            self.set_multiplicity_b(MultiplicityEnum.UNBOUND)
                    if current_value_b == past_value_b:
                        if current_value_a != past_value_a:
                            self.set_multiplicity_a(MultiplicityEnum.UNBOUND)
            encountered_a.append(current_value_a)
            encountered_b.append(current_value_b)
        self.set_inst_level_order()

    def set_inst_level_order(self):
        if self.multiplicity_a == MultiplicityEnum.ONE and self.multiplicity_b == MultiplicityEnum.ONE:
            self.inst_level_order = InstLevelOrder.SAME
        else:
            if self.multiplicity_a == MultiplicityEnum.UNBOUND and self.multiplicity_b == MultiplicityEnum.ONE:
                self.inst_level_order = InstLevelOrder.LOWER
            else:
                if self.multiplicity_a == MultiplicityEnum.ONE and self.multiplicity_b == MultiplicityEnum.UNBOUND:
                    self.inst_level_order = InstLevelOrder.HIGHER
                else:
                    self.inst_level_order = InstLevelOrder.UNDEFINED

    def get_lower_or_equals(self) -> bool:
        if self.inst_level_order == InstLevelOrder.LOWER or self.inst_level_order == InstLevelOrder.SAME:
            return True
        else:
            return False

    def get_higher_or_equals(self) -> bool:
        if self.inst_level_order == InstLevelOrder.HIGHER or self.inst_level_order == InstLevelOrder.SAME:
            return True
        else:
            return False


    def __repr__(self):
        return (f"{self.property_a} <-> {self.property_b} ({self.inst_level_order.value}:"
                f" {self.multiplicity_a.value} <-> {self.multiplicity_b.value})")