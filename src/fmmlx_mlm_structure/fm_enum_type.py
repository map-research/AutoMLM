import xml.etree.ElementTree as ElementTree


class FmmlxEnumType:
    def __init__(self, enum_name: str):
        self.enum_name = enum_name
        self.enum_values = []

    def add_enum_value(self, enum_value: str):
        self.enum_values.append(enum_value)

    def __repr__(self):
        enum_print: str = ""
        enum_print = f"[ENUM] {self.enum_name}: "
        for enum_value in self.enum_values:
            enum_print += f"{enum_value}, "
        return enum_print[:-2]

    def export(self, root: ElementTree.Element):
        model = root.find('Model')
        addEnum = ElementTree.SubElement(model, 'addEnumeration', name=self.enum_name)
        for value in self.enum_values:
            addEnumValue = ElementTree.SubElement(model, 'addEnumerationValue', enum_name=self.enum_name,
                                                  enum_value_name=str(value))
        return root