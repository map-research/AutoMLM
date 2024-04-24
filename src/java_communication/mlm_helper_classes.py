from typing import List
import xml.etree.ElementTree as ET

# This file specifies all classes within an MLM.


class EnumType:
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
    
    def export(self, root: ET.Element):
        model = root.find('Model')
        addEnum = ET.SubElement(model, 'addEnumeration', name=self.enum_name)
        for value in self.enum_values:
            addEnumValue = ET.SubElement(model, 'addEnumerationValue', enum_name=self.enum_name, enum_value_name=str(value))
        return root



class MlmAttr:
    def __init__(self, attr_name: str, attr_type: str, inst_level: int,
                 uses_enum: bool = False, uses_domain_specific_type: bool = False):
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.attr_type_short = attr_type.split("::")[2]
        self.inst_level = inst_level
        self.uses_enum = False
        self.uses_domain_specific_type = False
        self.name_of_owner_class: str = ""

    def set_enum_type(self, enum_type: EnumType):
        self.attr_type_short = enum_type.enum_name
        self.uses_enum = True

    def set_name_of_owner_class(self, name_of_owner_class: str):
        self.name_of_owner_class = name_of_owner_class

    def __repr__(self):
        return f"[ATTR-{self.inst_level}] {self.attr_name}:{self.attr_type_short}"


class MlmSlot:
    def __init__(self, slot_name: str, value: str):
        self.attribute = None
        self.slot_name = slot_name
        self.value = value # self._import_slot_value(value)

    def set_attribute(self, attr: MlmAttr):
        self.attribute = attr

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
        return f"[SLOT] {self.slot_name}:{self.value}"


class MlmOperation:
    def __init__(self, operation_name: str, inst_level: int, return_type: str):
        self.operation_name = operation_name
        self.inst_level = inst_level
        self.return_type = return_type

    def __repr__(self):
        return f"[OP-{self.inst_level}] {self.operation_name}():{self.return_type}"


class MlmConstraint:

    def __init__(self, constraint_name: str, inst_level: int):
        self.constraint_name = constraint_name
        self.inst_level = inst_level

    def __repr__(self):
        return f"[CONST-{self.inst_level}] {self.constraint_name}"


class MlmObject:
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
    

    def set_class_of_object(self, new_class_of_object):
        self.class_of_object = new_class_of_object
        self.level = int(new_class_of_object.level) - 1

    def add_attr(self, attr: MlmAttr):
        self.attr_list.append(attr)

    def add_slot(self, slot: MlmSlot):
        self.slot_list.append(slot)

    def add_operation(self, operation: MlmOperation):
        self.operations_list.append(operation)

    def add_constraint(self, constraint: MlmConstraint):
        self.constraints_list.append(constraint)

    def export(self, root):
        projectName = root.attrib['path']

        diagrams = root.find('Diagrams')
        diagram = diagrams.find('Diagram')
        instances = diagram.find('Instances')
        # TODO good placement
        instance = ET.SubElement(instances, 'Instance', hidden='false', path=projectName+"::"+self.name, xCoordinate='0', yCoordinate='0')

        model = root.find('Model')
        
        if self.class_of_object == None:
            metaClass = ET.SubElement(model, 'addMetaClass', abstract=self.is_abstract, level=str(self.level), maxLevel=str(self.level), name=self.name, package=projectName, singleton='false')
        else:
            instance = ET.SubElement(model, 'addInstance', abstract=self.is_abstract, level=str(self.level), maxLevel=str(self.level), name=self.name, of=self.class_of_object.full_name, package=projectName, singleton='false')

        for attr in self.attr_list:
            attribute = ET.SubElement(model, 'addAttribute',level=str(attr.inst_level), multiplicity='Seq{1,1,true,false}',name=attr.attr_name, package=projectName, type=attr.attr_type )
            # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
            attribute.set('class', projectName+"::"+self.name)

        for slot in self.slot_list:
            slot = ET.SubElement(model, 'changeSlotValue', package = projectName, slotName = slot.attribute.attr_name ,valueToBeParsed=slot.value)
            # this attr has to be set separetly because of the keyword class and cannot be used in the prior operation
            slot.set('class', projectName+self.name)           

        for constraint in self.constraints_list:
            constraint = ET.SubElement(model, 'addConstraint', body='true', constName=constraint.constraint_name, instLevel=str(constraint.inst_level), package=projectName, reason='"This constraint fails"')
            constraint.set('class', projectName+"::"+self.name)

        for operation in self.operations_list:
            operation = ET.SubElement(model, 'addOperation', body='@Operation '+operation.operation_name+' [monitor=false,delToClassAllowed=false]():XCore::'+operation.return_type+' null end', 
                                    level=str(operation.inst_level), monitored='false', name=operation.operation_name, package=projectName, paramNames='', paramTypes='', type=operation.return_type)
            operation.set('class', projectName+"::"+self.name)

    def set_is_abstract(self, is_abstract: bool):
        self.is_abstract = is_abstract

    def add_parent_class(self, parent_class):
        self.parent_classes.append(parent_class)

    def is_specialization(self) -> bool:
        return not self.parent_classes


class Cardinality:
    def __init__(self, min_card: int, max_card: int, is_unbounded: bool = False) -> None:
        self.min_card = min_card
        self.max_card = max_card
        self.is_unbounded = is_unbounded

    def __repr__(self):
        print(self.is_unbounded)
        max_card_str = "*" if self.is_unbounded else f"{self.max_card}"
        return f"({self.min_card}, {max_card_str})"


class MlmAssociation:
    def __init__(self, name: str, source_inst_level: int, target_inst_level: int):
        self.name = name
        self.source_inst_level = source_inst_level
        self.target_inst_level = target_inst_level
        self.source_class: MlmObject = None
        self.target_class: MlmObject = None
        self.source_multiplicity: Cardinality = None
        self.target_multiplicity: Cardinality = None

    def set_source_class(self, source_class):
        self.source_class = source_class

    def set_target_class(self, target_class):
        self.target_class = target_class

    def set_source_multiplicity(self, min_card: int, max_card: int):
        if max_card == -1:
            self.source_multiplicity = Cardinality(min_card, max_card, is_unbounded=True)
            # IMPORTANT: DOES NOT WORK IF CONTINGENT ASSOCIATIONS ARE PRESENT
        else:
            self.source_multiplicity = Cardinality(min_card, max_card)

    def set_target_multiplicity(self, min_card: int, max_card: int):
        if max_card == -1:
            self.target_multiplicity = Cardinality(min_card, max_card, is_unbounded=True)
            # IMPORTANT: DOES NOT WORK IF CONTINGENT ASSOCIATIONS ARE PRESENT
        else:
            self.target_multiplicity = Cardinality(min_card, max_card)

    def __repr__(self):
        return (f"[ASSOCIATION {self.name}] From {self.source_class.name} (at L{self.source_inst_level})"
                f" to {self.target_class.name} (at L{self.target_inst_level})")
                # f"\n {self.source_multiplicity} {self.source_class.name}"
                # f" {self.name} {self.target_class.name}")
    
    def export(self, root: ET.Element):
        projectName = root.attrib['path']
        model = root.find('Model') 
        # transform of cardinalities needed
        multSourceToTarget = 'Seq{' + str(self.target_multiplicity.min_card) +',' + str(self.target_multiplicity.max_card) + ',true,false}'
        multTargetToSource = 'Seq{' + str(self.source_multiplicity.min_card) +',' + str(self.source_multiplicity.max_card) + ',false,false}'

        addAssoc = ET.SubElement(model, 'addAssociation',accessSourceFromTargetName=self.source_class.name.lower(), 
                                accessTargetFromSourceName=self.target_class.name.lower(), classSource=self.source_class.full_name, 
                                classTarget=self.target_class.full_name, fwName=self.name, instLevelSource=str(self.source_inst_level), 
                                instLevelTarget=str(self.target_inst_level), multSourceToTarget=multSourceToTarget, 
                                multTargetToSource=multTargetToSource, package=projectName,reverseName='-1', sourceVisibleFromTarget='false', 
                                targetVisibleFromSource='true')
        return root


class MlmLink:
    def __init__(self, name: str):
        self.name = name
        self.source_object: MlmObject = None
        self.target_object: MlmObject = None

    def set_source_object(self, source_object: MlmObject):
        self.source_object = source_object

    def set_target_object(self, target_object: MlmObject):
        self.target_object = target_object

    def __repr__(self):
        return f"[LINK {self.name}] From {self.source_object.name} to {self.target_object.name}"

