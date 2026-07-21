from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.model_property import ModelProperty

# from src.fmmlx_mlm_structure.fm_object import FmmlxObject

'''
FmmlxSlot serves as an implementation of slots in FMMLx. Note that the attribute "owner" is of type FmmlxObject.
Thus the method set_attribute() can call "class_of_object".

You MAY NOT import FmmlxObject, though. This causes a circular import.
'''


class FmmlxSlot(ModelProperty):
    def __init__(self, slot_name: str, value: str):
        super().__init__(print_name=f"{slot_name}:{value}")
        self.attribute = None
        self.slot_name = slot_name
        self.value = value # self._import_slot_value(value) # parsing done in FmmlxModel class
        self.owner = None
        self.slot_category: str = "SLOT"

    def is_multi_valued(self):
        return "///" in str(self.value)

    def get_values_as_list(self) -> [str]:
        return str(self.value).split("///")

    def set_attribute(self, attribute: FmmlxAttribute = None):
        # Beim CSV-Import kennen wir das passende Attribut schon.
        if attribute is not None:
            self.attribute = attribute
            return

        # Beim XML-Import wird das passende Attribut gesucht.
        for attr in self.owner.class_of_object.get_all_attributes():
            if attr.attr_name == self.slot_name:
                self.attribute = attr

    def get_attribute(self):
        return self.attribute

    def set_owner_object(self, owner):
        self.owner = owner

    def get_owner_object(self):
        return self.owner

    def get_value(self):
        return self.value

    def _import_slot_value(self, slot_value: str) -> str:
        # IMPORT STR
        if slot_value[-10:] == "asString()":
            print("STRING")
            # print(slot_value[1:-12].split(sep=","))
        else:
            if slot_value[11:].startswith("Date"):
                print("DATE")

        # MAYBE: do real type? int as int float as flot, date as date etc

        return slot_value

    def __repr__(self):
        return f"[{self.slot_category}] {self.slot_name}: {self.value}"
