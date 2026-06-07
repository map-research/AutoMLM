"""
Slot collectives are used in property-precedence analysis. Instances of slot collectives represent groupings of slots
for unique values within a specific attribute.
"""
from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.fm_slot import FmmlxSlot


class SlotCollective:
    def __init__(self, value: str, attribute: FmmlxAttribute):
        self.value: str = value
        self.attribute: FmmlxAttribute = attribute
        self.slots: [FmmlxSlot] = []
        self.scope_list: [] = []
        self.scope_set: set = set()

    def get_class(self):
        return self.attribute.get_owner()

    def add_object_to_scope(self, fm_object):
        self.scope_list.append(fm_object)

    def get_attribute(self) -> FmmlxAttribute:
        return self.attribute

    def get_value(self) -> str:
        return self.value

    def add_slot(self, slot: FmmlxSlot):
        self.slots.append(slot)

    def get_scope_set(self) -> set:
        return set(self.scope_list)

    def __le__(self, other):
        """
        <= operator implemented to return slot precedence a <= b, reads as a precedes b (if b, then a)
        """
        return self.get_scope_set() <= other.get_scope_set()

    def __ge__(self, other):
        return self.get_scope_set() >= other.get_scope_set()

    def __gt__(self, other):
        return self.get_scope_set() > other.get_scope_set()

    def __lt__(self, other):
        return self.get_scope_set() < other.get_scope_set()

    def compare(self, other) -> str:
        """
        the compare method compares two SlotCollective instances and returns whether the respective symbol
        """
        if self < other:
            return "<"
        elif self > other:
            return ">"
        elif self >= other >= self:
            return "="
        else:
            return "!="  # != in this context means disjoint


    def pretty_print_scope(self) -> str:
        pp_scope: str = ""
        for fm_object in self.scope_list:
            pp_scope += fm_object.get_object_name() if pp_scope == "" else ", " + fm_object.get_object_name()
        return pp_scope

    def __repr__(self):
        return f"[SlotCollective] {self.attribute.attr_name}:\"{self.value}\": {{{self.pretty_print_scope()}}}]"
