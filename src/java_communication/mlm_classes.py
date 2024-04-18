from typing import List


# This file specifies all classes within an MLM.
class MlmAttr:
    def __init__(self, attr_name: str, attr_type: str, inst_level):
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.attr_type_short = attr_type.split("::")[2]
        self.inst_level = inst_level

    def __repr__(self):
        return f"[ATTR-{self.inst_level}] {self.attr_name}:{self.attr_type_short}"


class MlmSlot:
    def __init__(self, attr: MlmAttr, value: str):
        self.attr = attr
        self.value = value

    def __repr__(self):
        return f"[SLOT] {self.attr.attr_name}:{self.value}"


class MlmObject:
    def __init__(self, full_name: str, name: str, level: int, attr_list: List[MlmAttr], slot_list: List[MlmSlot],
                 class_of_object):
        self.full_name = full_name
        self.name = name
        self.level = level
        self.attr_list = attr_list
        self.slot_list = slot_list
        self.class_of_object = class_of_object

    def __repr__(self):
        # class_str = f"[CLASS] {self.name}"
        # attr_str = ""
        # for attr in self.attr_list:
        #    attr_str  += ""
        print(f"[L{self.level}-OBJECT] {self.name} [of {self.class_of_object.name}]")
        print(*self.attr_list, sep="\n")
        print(*self.slot_list, sep="\n")
        return ""

    def set_class_of_object(self, new_class_of_object):
        self.class_of_object = new_class_of_object
        self.level = int(new_class_of_object.level) - 1

    def _get_meta_class(self):
        return self("MetaClass", "MetaClass", 99, [], [], object())
