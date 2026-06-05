from src.fmmlx_mlm_structure.fm_enum_type import FmmlxEnumType


class FmmlxAttribute:
    def __init__(self, attr_name: str, attr_type: str, inst_level: int,
                 uses_enum: bool = False, uses_domain_specific_type: bool = False):
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.attr_type_short = attr_type.split("::")[2]
        self.inst_level = inst_level
        self.uses_enum = False
        self.uses_domain_specific_type = False
        self.name_of_owner_class: str = ""
        self.lexemes = []

    def set_enum_type(self, enum_type: FmmlxEnumType):
        self.attr_type_short = enum_type.enum_name
        self.uses_enum = True

    def set_name_of_owner_class(self, name_of_owner_class: str):
        self.name_of_owner_class = name_of_owner_class

    def __repr__(self):
        return f"[ATTR-{self.inst_level}] {self.attr_name}:{self.attr_type_short}"
