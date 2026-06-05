import xml.etree.ElementTree as ElementTree
from typing import List
from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.fm_constraint import FmmlxConstraint
from src.fmmlx_mlm_structure.fm_operation import FmmlxOperation
from src.fmmlx_mlm_structure.fm_slot import FmmlxSlot


class FmmlxObject:
    def __init__(self, full_name: str, name: str, level: str, class_of_object, is_abstract: str):
        self.full_name = full_name
        self.name = name
        self.level: int = int(level)
        self.attr_list = []
        self.slot_list = []
        self.operations_list = []
        self.constraints_list = []
        self.class_of_object = class_of_object
        self.is_abstract: bool = True if is_abstract == "true" else False
        self.parent_classes = []

    def __repr__(self):
        # class_str = f"[CLASS] {self.name}"
        # attr_str = ""
        # for attr in self.attr_list:
        #    attr_str  += ""
        print("ABSTRACT CLASS") if self.is_abstract else None
        print(f"[L{self.level}-OBJECT] {self.name} [of {self.class_of_object.name}]")
        print(f"HAS {len(self.parent_classes)} PARENTS") if self.parent_classes else None
        print(*self.attr_list, sep="\n")
        print(*self.slot_list, sep="\n")
        print(*self.operations_list, sep="\n")
        print(*self.constraints_list, sep="\n")
        return ""

    @classmethod
    def meta_class(cls):
        return cls("MetaClass", "MetaClass", "99",
                   FmmlxObject("MetaClass", "MetaClass", "100", None, "False")
                   , "False")

    @classmethod
    def get_shell_class(cls, base_class):
        return cls(base_class.full_name, base_class.name, "0", cls.meta_class(), "false")

    def get_all_slots(self) -> List[FmmlxSlot]:
        return self.slot_list

    def get_all_attributes(self) -> List[FmmlxAttribute]:
        return self.attr_list

    def set_class_of_object(self, new_class_of_object):
        self.class_of_object = new_class_of_object
        self.level = int(new_class_of_object.level) - 1

    def add_attr(self, attr: FmmlxAttribute):
        self.attr_list.append(attr)

    def add_slot(self, slot: FmmlxSlot):
        self.slot_list.append(slot)

    def add_operation(self, operation: FmmlxOperation):
        self.operations_list.append(operation)

    def add_constraint(self, constraint: FmmlxConstraint):
        self.constraints_list.append(constraint)

    def set_level(self, level: int):
        self.level = level

    def export(self, root):
        projectName = root.attrib['path']
        diagrams = root.find('Diagrams')
        diagram = diagrams.find('Diagram')
        instances = diagram.find('Instances')
        # TODO good placement
        instance = ElementTree.SubElement(instances, 'Instance', hidden='false', path=projectName + "::" + self.name,
                                          xCoordinate='0', yCoordinate='0')

        model = root.find('Model')

        if self.class_of_object == None or self.class_of_object.name == 'MetaClass':
            metaClass = ElementTree.SubElement(model, 'addMetaClass', abstract='false', level=str(self.level),
                                               maxLevel=str(self.level), name=self.name, package=projectName,
                                               singleton='false')
        else:
            # adapt ofname to new projectName
            ofName = projectName + "::" + self.class_of_object.full_name.split("::")[2]
            instance = ElementTree.SubElement(model, 'addInstance', abstract='false', level=str(self.level),
                                              maxLevel=str(self.level), name=self.name, of=ofName, package=projectName,
                                              singleton='false')

        for attr in self.attr_list:
            attribute = ElementTree.SubElement(model, 'addAttribute', level=str(attr.inst_level),
                                               multiplicity='Seq{1,1,true,false}', name=attr.attr_name,
                                               package=projectName, type=attr.attr_type)
            # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
            attribute.set('class', projectName + "::" + self.name)

        for slot in self.slot_list:
            slot = ElementTree.SubElement(model, 'changeSlotValue', package=projectName,
                                          slotName=slot.attribute.attr_name, valueToBeParsed=slot.value)
            # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
            slot.set('class', projectName + self.name)

        for constraint in self.constraints_list:
            constraint = ElementTree.SubElement(model, 'addConstraint', body='true',
                                                constName=constraint.constraint_name,
                                                instLevel=str(constraint.inst_level), package=projectName,
                                                reason='"This constraint fails"')
            constraint.set('class', projectName + "::" + self.name)

        for operation in self.operations_list:
            operation = ElementTree.SubElement(model, 'addOperation',
                                               body='@Operation ' + operation.operation_name + ' [monitor=false,delToClassAllowed=false]():XCore::' + operation.return_type + ' null end',
                                               level=str(operation.inst_level), monitored='false',
                                               name=operation.operation_name, package=projectName, paramNames='',
                                               paramTypes='', type=operation.return_type)
            operation.set('class', projectName + "::" + self.name)

        for parent in self.parent_classes:
            parent = ElementTree.SubElement(model, 'changeParent', new=projectName + "::" + parent.name, old="",
                                            package=projectName)
            parent.set('class', projectName + "::" + self.name)

    def set_is_abstract(self, is_abstract: bool):
        self.is_abstract = is_abstract

    def add_parent_class(self, parent_class):
        self.parent_classes.append(parent_class)

    def is_specialization(self) -> bool:
        return not self.parent_classes