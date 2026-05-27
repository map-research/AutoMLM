from typing import List

from src.mlm_class import *
from src.mlm_helper_classes import *
from itertools import permutations
from enum import Enum
from PropertyPrecedenceGraph import *


class InstantiationLevelOrder(Enum):
    LOWER = "<"
    SAME = "="
    HIGHER = ">"


class MultiLevelModelAnalyzer:
    def __init__(self, flat_model: MultilevelModel):
        self.flat_model = flat_model
        self.deep_model: MultilevelModel = MultilevelModel()

    def analyze_attribute_precedence_for_class(self, mlm_class: MlmObject):
        all_instances: List[MlmObject] = self.flat_model.get_all_objects_for_class(mlm_class)
        all_attributes_of_class = mlm_class.get_all_attributes()
        all_slots: List[MlmSlot] = []
        all_slot_lists: List[List[MlmSlot]] = []

        # STEP 1: EXTRACT ALL SLOT VALUES

        for instance in all_instances:
            all_slots = instance.get_all_slots()
            slots_for_object: List = []
            for slot in all_slots:
                slots_for_object.append(slot.value)
            all_slot_lists.append(slots_for_object)

        #STEP 2: GROUP SLOT VALUES PER ATTRIBUTE
        attribute_value_lists = [list([all_attributes_of_class[i], attribute_values])
                                 for i, attribute_values in enumerate(zip(*all_slot_lists), start=0)]

        # STEP 3: COMPARE ALL GROUPED ATTRIBUTES WITH EACH OTHER
        all_attribute_pairs = permutations(iterable=attribute_value_lists, r=2)

        co_dependency_array = []

        for attribute_pair in all_attribute_pairs:
            attribute_group_one = attribute_pair[0][1]
            attribute_group_two = attribute_pair[1][1]

            attribute_one = attribute_pair[0][0]
            attribute_two = attribute_pair[1][0]

            # CASE 1: IS BIJECTIVE
            if self._is_bijective(attribute_group_one, attribute_group_two):
                co_dependency_array.append((attribute_one, attribute_two, InstantiationLevelOrder.SAME))
            # CASE 2: IS SURJECTIVE
            elif self._is_surjective(attribute_group_one, attribute_group_two):
                co_dependency_array.append((attribute_one, attribute_two, InstantiationLevelOrder.LOWER))
            # CASE 3: IS INJECTIVE
            else:
                co_dependency_array.append((attribute_one, attribute_two, InstantiationLevelOrder.HIGHER))

        print(*co_dependency_array, sep="\n")
        #STEP 4: IDENTIFY LOWEST ATTRIBUTES INST LEVEL

        from collections import defaultdict, deque

        # Union-Find setup for SAME-level grouping
        parent = {}

        def find(x):
            while parent.get(x, x) != x:
                parent[x] = parent.get(parent[x], parent[x])
                x = parent[x]
            return x

        def union(x, y):
            parent[find(x)] = find(y)

        for a1, a2, relation in co_dependency_array:
            if relation == InstantiationLevelOrder.SAME:
                union(a1, a2)

        def get_group(x):
            return find(x)

        # Build group mapping (group representative → set of equivalent attributes)
        grouped_attributes = defaultdict(set)
        all_attributes = set()
        for a1, a2, _ in co_dependency_array:
            all_attributes.update([a1, a2])
        for attr in all_attributes:
            grouped_attributes[get_group(attr)].add(attr)

        # Build dependency graph for ordering
        graph = defaultdict(set)
        in_degree = defaultdict(int)

        for a1, a2, relation in co_dependency_array:
            g1 = get_group(a1)
            g2 = get_group(a2)
            if g1 == g2:
                continue  # Skip internal SAME relations
            if relation == InstantiationLevelOrder.LOWER:
                if g2 not in graph[g1]:
                    graph[g1].add(g2)
                    in_degree[g2] += 1
            elif relation == InstantiationLevelOrder.HIGHER:
                if g1 not in graph[g2]:
                    graph[g2].add(g1)
                    in_degree[g1] += 1

        # Include all groups, even if isolated (no edges)
        all_groups = set(grouped_attributes.keys())

        # Topological sort
        queue = deque([group for group in all_groups if in_degree[group] == 0])
        ordered_groups = []

        while queue:
            current = queue.popleft()
            ordered_groups.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Detect remaining (disconnected or cyclic) groups not visited
        visited_groups = set(ordered_groups)
        remaining_groups = all_groups - visited_groups
        ordered_groups.extend(sorted(remaining_groups, key=lambda g: sorted(attr.attr_name for attr in grouped_attributes[g])))

        print("\nAttribute order from lowest to highest (grouped by SAME):\n")
        deep_class_level: int = 0
        new_attributes: List[MlmAttr] = []
        for i, group in enumerate(ordered_groups, start=0):
            #print(f"Instantiation Level {i}: {grouped_attributes[group]}")
            for old_attr in grouped_attributes[group]:
                deep_attr = MlmAttr(old_attr.attr_name, old_attr.attr_type, i)
                new_attributes.append(deep_attr)
            deep_class_level += 1
            print(f"Instantiation Level {i}:")
            print(" = ".join(sorted(attr.attr_name for attr in grouped_attributes[group])))

        #STEP 5: Create new Class
        deep_class: MlmObject = MlmObject(mlm_class.full_name, mlm_class.name, str(deep_class_level),
                                          MlmObject.meta_class(), "False")

        for new_attr in new_attributes:
            deep_class.add_attr(new_attr)

        print("\n")
        print(deep_class)

    def _is_bijective(self, seq1, seq2):
        distinct1 = set(seq1)
        distinct2 = set(seq2)
        distinctMappings = set(zip(seq1, seq2))
        return len(distinct1) == len(distinct2) == len(distinctMappings)

    def _is_surjective(self, a, b):
        # Step 1: Ensure both lists have the same length
        if len(a) != len(b):
            return False

        # establish a set
        c = {}

        # iterate over every attr
        for i in range(len(a)):
            # if the slot value is already in the set ...
            if a[i] in c.keys():
                # ... it has to be the same value as before
                if c[a[i]] == b[i]:
                    # if so thats fine
                    pass
                else:
                    # if not .. we dont have a surjective relation
                    return False
            else:
                # if the slot value did not occur yet, it will be added
                c[a[i]] = b[i]

        return True

    def model_deepening(self, all_classes: bool, single_class_name: str = ""):
        if all_classes:
            for i, flat_class in enumerate(self.flat_model.get_all_flat_classes(), start = 0):
                print(
                    f"------------------------------------------------------------------------------------------------\n"
                    f"ANALYZING ATTRIBUTE CO-DEPENDENCY FOR CLASS <{flat_class.name}>\n")
                self.attribute_codependency_analysis(flat_class)
        else:
            if single_class_name == "":
                print(f"NO CLASS TO ANALYZE PROVIDED!")
            else:
                self.attribute_codependency_analysis(self.flat_model.get_mlm_object_by_shortname(single_class_name))
        print(self.deep_model)

    def attribute_codependency_analysis(self, flat_class: MlmObject):
        co_dependency_graph: CoDependencyGraph = self.construct_attribute_codependency_graph(flat_class)
        co_dependency_graph.perform_multiplicity_analysis()
        flat_class.set_cod_graph(co_dependency_graph)
        self.construct_deep_hierarchy_for_class(flat_class)

    def construct_deep_hierarchy_for_class(self, flat_class: MlmObject):
        assert flat_class.get_cod_graph() is not None  # as a pre-condition
        deepest_class: MlmObject = MlmObject.get_shell_class(flat_class)
        deepest_level: int = 0
        attr_dict = {}
        all_instances: List[MlmObject] = self.flat_model.get_all_objects_for_class(flat_class)

        for mlm_attr in flat_class.get_cod_graph().get_reordered_mlm_attributes():
            # dict entry currently overrides each time
            attr_dict.update({mlm_attr.inst_level: mlm_attr})
            deepest_class.add_attr(mlm_attr)
            if mlm_attr.inst_level >= deepest_level:
                deepest_level = mlm_attr.inst_level + 1

        deepest_class.set_level(deepest_level)
        self.deep_model.add_mlm_object(deepest_class)

        level_iterator: int = deepest_level
        value_lists = self._get_attribute_value_lists_for_class(flat_class)

        while level_iterator > 0:
            level_iterator -= 1
            attr_for_current_level: List[MlmAttr] = []
            num_of_instances: int = 0
            all_level_values = []
            zipped_level_values = ()

            for attr in deepest_class.get_all_attributes():
                if attr.inst_level == level_iterator:
                    attr_for_current_level.append(attr)
            for level_attr in attr_for_current_level:
                for value_list in value_lists:
                    if level_attr.attr_name == value_list[0].attr_name:
                        all_level_values.append(value_list[1])
            zipped_level_values = set(zip(*all_level_values))
            new_instance_name: str = ""
            for unique_value_set in zipped_level_values:
                new_instance_name = self._get_new_instance_name(unique_value_set)
                new_instance: MlmObject = MlmObject(new_instance_name, new_instance_name, str(level_iterator),
                                                    deepest_class, "false")
                for current_attr, attr_values in zip(attr_for_current_level, all_level_values):
                    print(current_attr)
                    print(attr_values)
                    new_slot: MlmSlot = MlmSlot(current_attr.attr_name, "dummy_value")
                    new_slot.set_attribute(current_attr)
                    new_instance.add_slot(new_slot)
                print(new_instance_name)
                print(attr_for_current_level)
                print(all_level_values)
                print("-------------------------------")
                self.deep_model.add_mlm_object(new_instance)
                num_of_instances += 1
            #print(num_of_instances)

    def _get_new_instance_name(self, unique_values: List[str]) -> str:
        new_instance_name: str = ""
        if len(unique_values) > 1:
            for unique_value in unique_values:
                new_instance_name += unique_value.title() # results in camel case since spaces must not be present
                new_instance_name += "_"
        else:
            new_instance_name = unique_values[0]

        if new_instance_name.endswith("_"):
            new_instance_name = new_instance_name[:-1]

        return new_instance_name

    def _get_attribute_value_lists_for_class(self, mlm_class: MlmObject):
        all_instances: List[MlmObject] = self.flat_model.get_all_objects_for_class(mlm_class)
        all_attributes_of_class = mlm_class.get_all_attributes()
        all_slots: List[MlmSlot] = []
        all_slot_lists: List[List[MlmSlot]] = []

        # STEP 1: EXTRACT ALL SLOT VALUES

        for instance in all_instances:
            all_slots = instance.get_all_slots()
            slots_for_object: List = []
            for slot in all_slots:
                slots_for_object.append(slot.value)
            all_slot_lists.append(slots_for_object)

        # STEP 2: GROUP SLOT VALUES PER ATTRIBUTE
        attribute_value_lists = [list([all_attributes_of_class[i], attribute_values])
                                 for i, attribute_values in enumerate(zip(*all_slot_lists), start=0)]

        return attribute_value_lists

    # new implementation of dependency analysis with dependency graph and dominance analysis (Sep 10, 2025)
    def construct_attribute_codependency_graph(self, mlm_class: MlmObject) -> CoDependencyGraph:
        co_dependency_graph: CoDependencyGraph = CoDependencyGraph(self._get_attribute_value_lists_for_class(mlm_class))
        return co_dependency_graph

