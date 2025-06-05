from typing import List

from src.mlm_class import *
from src.mlm_helper_classes import *
from itertools import permutations
from enum import Enum

class InstLevelOrder(Enum):
    LOWER = "<"
    SAME = "="
    HIGHER = ">"


class MultiLevelModelAnalyzer():
    def __init__(self, flat_model: MultilevelModel):
        self.flat_model = flat_model

    def analyze_attribute_dependency_for_class(self, mlm_class: MlmObject):
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

        all_attribute_comparisons = []

        for attribute_pair in all_attribute_pairs:
            attribute_group_one = attribute_pair[0][1]
            attribute_group_two = attribute_pair[1][1]

            attribute_one = attribute_pair[0][0]
            attribute_two = attribute_pair[1][0]

            if self._is_bijective(attribute_group_one, attribute_group_two):
                all_attribute_comparisons.append((attribute_one, attribute_two, InstLevelOrder.SAME))
            elif self._is_surjective(attribute_group_one, attribute_group_two):
                all_attribute_comparisons.append((attribute_one, attribute_two, InstLevelOrder.LOWER))
            else:
                all_attribute_comparisons.append((attribute_one, attribute_two, InstLevelOrder.HIGHER))

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

        for a1, a2, relation in all_attribute_comparisons:
            if relation == InstLevelOrder.SAME:
                union(a1, a2)

        def get_group(x):
            return find(x)

        # Build group mapping (group representative → set of equivalent attributes)
        grouped_attributes = defaultdict(set)
        all_attributes = set()
        for a1, a2, _ in all_attribute_comparisons:
            all_attributes.update([a1, a2])
        for attr in all_attributes:
            grouped_attributes[get_group(attr)].add(attr)

        # Build dependency graph for ordering
        graph = defaultdict(set)
        in_degree = defaultdict(int)

        for a1, a2, relation in all_attribute_comparisons:
            g1 = get_group(a1)
            g2 = get_group(a2)
            if g1 == g2:
                continue  # Skip internal SAME relations
            if relation == InstLevelOrder.LOWER:
                if g2 not in graph[g1]:
                    graph[g1].add(g2)
                    in_degree[g2] += 1
            elif relation == InstLevelOrder.HIGHER:
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
