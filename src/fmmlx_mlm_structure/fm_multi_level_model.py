from enum import EnumMeta
from xml.dom.minidom import parse
from src.fmmlx_mlm_structure import xml_export as export_xml
from typing import List
import csv

from src.fmmlx_mlm_structure.fm_association import FmmlxAssociation
from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute
from src.fmmlx_mlm_structure.fm_constraint import FmmlxConstraint
from src.fmmlx_mlm_structure.fm_enum_type import FmmlxEnumType
from src.fmmlx_mlm_structure.fm_link import FmmlxLink
from src.fmmlx_mlm_structure.fm_object import FmmlxObject
from src.fmmlx_mlm_structure.fm_operation import FmmlxOperation
from src.fmmlx_mlm_structure.fm_slot import FmmlxSlot
from src.fmmlx_mlm_structure.multiplicity import Multiplicity

metaClass = FmmlxObject("MetaClass", "MetaClass", "99", None, "false")


class FmmlxModel:
    """
    This class serves to represent complete MultiLevelModels. It offers functions for importing standard FMMLx XML files
    into a Python representation and exporting them again to XML documents once processed as intended.
    All elements within a multi-level model are themselves instances of Python classes specified in mlm_helper_classes.py
    """

    def __init__(self, xml_file_path: str = "", csv_file_path: str = "", print_progress: bool = False):
        self.path_name = ""
        self.mlm_objects: List[FmmlxObject] = []
        self.enums: List[FmmlxEnumType] = []
        self.associations: List[FmmlxAssociation] = []
        self.links: List[FmmlxLink] = []
        self.parsed_xml = None
        self.print_progress = print_progress
        if xml_file_path != "":
            self._parse_xml(xml_file_path)
        if csv_file_path != "":
            self._import_csv(csv_file_path)

    def _import_csv(self, csv_file_path: str):
        """
        import CSV as MultiLevelModel. Note that CSV imports only account for classes and objects; relationships
        between classes and objects are not accounted for.
        """
        all_mlm_objects = []
        with open(csv_file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0
            all_csv_attr = []
            for row in csv_reader:
                if line_count == 0:
                    mlm_class: FmmlxObject = FmmlxObject("long", "csv_class", "1", FmmlxObject.meta_class(),
                                                    "false")
                    for col_counter in range(len(row)):
                        value: str = row[col_counter].strip().strip("\"")
                        new_attr: FmmlxAttribute = FmmlxAttribute(value, "Root::XCore::String", 0)
                        all_csv_attr.append(new_attr)
                        mlm_class.add_attr(new_attr)

                    all_mlm_objects.append(mlm_class)
                else:
                    mlm_instance: FmmlxObject = FmmlxObject("long", "instance", "0", mlm_class, "false")
                    all_mlm_objects.append(mlm_instance)

                    for col_counter in range(len(row)):
                        value: str = row[col_counter].strip().strip("\"")
                        new_slot: FmmlxSlot = FmmlxSlot(all_csv_attr[col_counter].attr_name, value)
                        new_slot.set_attribute(all_csv_attr[col_counter])
                        mlm_instance.add_slot(new_slot)

                line_count += 1
        self._set_mlm_objects(all_mlm_objects)

    def _set_mlm_objects(self, mlm_objects: List[FmmlxObject]):
        self.mlm_objects = mlm_objects

    def add_mlm_object(self, mlm_object: FmmlxObject):
        self.mlm_objects.append(mlm_object)

    def set_instances_of_mlm_objects(self):
        mlm_classes: List[FmmlxObject] = []
        for mlm_object in self.mlm_objects:
            if mlm_object.level > 0:
                mlm_classes.append(mlm_object)
        for mlm_class in mlm_classes:
            objects_beneath: List[FmmlxObject] = self.get_all_objects_at_level_x(mlm_class.level-1)
            for object_beneath in objects_beneath:
                if object_beneath.class_of_object == mlm_class:
                    mlm_class.add_instance(object_beneath)

    def get_all_objects_at_level_x(self, level: int) -> List[FmmlxObject]:
        objects_at_level_x: List[FmmlxObject] = []
        for obj in self.mlm_objects:
            if obj.level == level:
                objects_at_level_x.append(obj)
        return objects_at_level_x

    def get_all_flat_classes(self) -> List[FmmlxObject]:
        return self.get_all_objects_at_level_x(1)

    def get_all_pure_objects(self) -> List[FmmlxObject]:
        return self.get_all_objects_at_level_x(0)

    def export_xml(self, filepath : str = 'export_test.xml', project_name='Root::Export'):
        # create the root
        root = export_xml.preamble(project_name)
        # export all objects
        for object in self.mlm_objects:
            object.export(root)

        for enum in self.enums:
           enum.export(root)
        
        for assoc in self.associations:
           assoc.export(root)

        for link in self.links:
           link.export(root)

        # xml is written and saved
        root = export_xml.writeXML(root, filepath)
        print('New XML created at ' + filepath)

        # root is returned in case it is needed ?!
        return root

    def _parse_xml(self, doc_file_path: str):
        document = None
        try:
            document = parse(doc_file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{doc_file_path}' was not found!")
        except:
            raise Exception(f"File '{doc_file_path}' could not be parsed!")

        self.parsed_xml = document
        self.extract_mlm_from_xml()

    @classmethod
    def input_xml_path(cls):
        print("BEGIN MLM EXTRACTION\nEnter the MLM Source Location:")
        loc = input()
        return cls(xml_file_path=loc)

    def import_xml(self, xml_file_path: str):
        assert self.parsed_xml is None, ("Multi-level model is already imported! "
                                         "Overriding of existing model is forbidden.")
        self._parse_xml(xml_file_path)
        self.extract_mlm_from_xml()
        if self.print_progress:
            print("Extraction completed successfully!")

    def extract_mlm_from_xml(self):
        self.path_name = self.retrieve_path_name()
        if self.print_progress:
            print("BEGIN MLM EXTRACTION")
        self.mlm_objects = self.retrieve_all_mlm_objects()
        self.set_instances_of_mlm_objects()
        if self.print_progress:
            print("ALL OBJECTS RETRIEVED")
        self._set_generalizations()
        if self.print_progress:
            print("ALL GENERALIZATIONS RETRIEVED")
        self.enums = self.retrieve_all_enums()
        if self.print_progress:
            print("ALL ENUMS RETRIEVED")
        self.retrieve_all_attributes()
        if self.print_progress:
            print("ALL ATTRIBUTES RETRIEVED")
        self.retrieve_all_slots()
        if self.print_progress:
            print("ALL SLOTS RETRIEVED")
        self.retrieve_all_operations()
        self.retrieve_all_constraints()
        self.retrieve_all_associations()
        self.retrieve_all_links()

    def retrieve_path_name(self) -> str:
        return self.parsed_xml.documentElement.getAttribute("path")

    def retrieve_all_mlm_objects(self) -> List[FmmlxObject]:
        """
        This operation retrieves all MLM objects/classes. First all highest-level classes are retrieved via the
        function `_retrieve_all_mlm_metaclass_objects.` This is important since they have a separate XML tag.
        Afterward, the remaining MLM objects are retrieved.
        """
        mlm_objects = self._retrieve_metaclass_objects()
        for instance_object in self._retrieve_instance_objects():
            instance_object.set_class_of_object(self._get_class_of_mlm_object(instance_object.class_of_object.full_name,
                                                                              mlm_objects))
            if self.print_progress:
                print(f"Object {instance_object.object_name} extracted.")
            mlm_objects.append(instance_object)
        return mlm_objects

    def _retrieve_metaclass_objects(self) -> List[FmmlxObject]:
        mlm_objects = []
        for object_element in self.parsed_xml.getElementsByTagName("addMetaClass"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = FmmlxObject(mlm_object_long, object_element.getAttribute("name"),
                                     object_element.getAttribute("level"), metaClass,
                                     object_element.getAttribute("abstract"))
            mlm_objects.append(mlm_object)

        return mlm_objects

    def _retrieve_instance_objects(self) -> List[FmmlxObject]:
        mlm_objects = []
        for object_element in self.parsed_xml.getElementsByTagName("addInstance"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = FmmlxObject(mlm_object_long, object_element.getAttribute("name"), 99,
                                     FmmlxObject(object_element.getAttribute("of"),
                                             "", 99, None, "false"),
                                     object_element.getAttribute("abstract"))
            mlm_objects.append(mlm_object)

        return mlm_objects

    def _get_class_of_mlm_object(self, full_object_name: str, mlm_instance_objects: List[FmmlxObject]) -> FmmlxObject:
        for object_elem in mlm_instance_objects:
            if object_elem.full_name == full_object_name:
                return object_elem

    def _set_generalizations(self):
        for parent_element in self.parsed_xml.getElementsByTagName("changeParent"):
            child_class: FmmlxObject = self.get_mlm_object_by_fullname(parent_element.getAttribute("class"))
            for parent_class_name in parent_element.getAttribute("new").split(","):
                child_class.add_parent_class(self.get_mlm_object_by_fullname(parent_class_name))

    def retrieve_all_enums(self):
        enums_tmp: List[FmmlxEnumType] = []
        for enum_element in self.parsed_xml.getElementsByTagName("addEnumeration"):
            enums_tmp.append(FmmlxEnumType(enum_element.getAttribute("name")))
        for enum_value_element in self.parsed_xml.getElementsByTagName("addEnumerationValue"):
            for enum_tmp in enums_tmp:
                if enum_value_element.getAttribute("enum_name") == enum_tmp.enum_name:
                    enum_tmp.add_enum_value(enum_value_element.getAttribute("enum_value_name"))
        return enums_tmp

    def retrieve_all_attributes(self):
        for attribute_element in self.parsed_xml.getElementsByTagName("addAttribute"):
            new_attr = FmmlxAttribute(attribute_element.getAttribute("name"), attribute_element.getAttribute("type"),
                                      attribute_element.getAttribute("level"))
            # need to look for custom attr data types: enums or custom class types
            if new_attr.attr_type.split("::")[1] != "XCore" and new_attr.attr_type.split("::")[1] != "Auxiliary":
                if not self._is_custom_attribute_type_an_enum(new_attr):
                    print("TO-DO: Custom Data Type " + new_attr.attr_type_short + " Detected") #TODO CUSTOM CLASS AS OBJECT
            for mlm_object in self.mlm_objects:
                if attribute_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_attr(new_attr)
                    new_attr.set_owner(mlm_object)

    def _is_custom_attribute_type_an_enum(self, mlm_attr: FmmlxAttribute) -> bool:
        # check 1: look if in list of enums
        for enum in self.enums:
            if enum.enum_name == mlm_attr.attr_type_short:
                mlm_attr.set_enum_type(enum)
                return True
        return False

    def retrieve_all_slots(self):
        for slot_element in self.parsed_xml.getElementsByTagName("changeSlotValue"):
            new_slot = FmmlxSlot(slot_element.getAttribute("slotName"),
                                 self._parse_slot_value(slot_element.getAttribute("valueToBeParsed")))
            for mlm_object in self.mlm_objects:
                if slot_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_slot(new_slot)
                    new_slot.set_owner_object(mlm_object)
                    new_slot.set_attribute()

    def _parse_slot_value(self, slot_value: str):
        if slot_value.endswith("asString()"):
            sign_list = slot_value[1:].split("]")[0].split(",")
            slot_value = ""
            if sign_list[0] != "":
                for sign_code in sign_list:
                    slot_value += chr(int(sign_code))
        return slot_value

    def retrieve_all_operations(self):
        for operations_element in self.parsed_xml.getElementsByTagName("addOperation"):
            new_operation = FmmlxOperation(operations_element.getAttribute("name"),
                                           operations_element.getAttribute("level"),
                                           operations_element.getAttribute("type"))

            for mlm_object in self.mlm_objects:
                if operations_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_operation(new_operation)

    def retrieve_all_constraints(self):
        for constraint_element in self.parsed_xml.getElementsByTagName("addConstraint"):
            new_constraint = FmmlxConstraint(constraint_element.getAttribute("constName"),
                                             constraint_element.getAttribute("instLevel"))
            for mlm_object in self.mlm_objects:
                if constraint_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_constraint(new_constraint)

    def retrieve_all_associations(self):
        for association_element in self.parsed_xml.getElementsByTagName("addAssociation"):
            new_association = FmmlxAssociation(association_element.getAttribute("fwName"),
                                               association_element.getAttribute("instLevelSource"),
                                               association_element.getAttribute("instLevelTarget"))
            tgt_mult = association_element.getAttribute("multSourceToTarget")[4:-1].split(",")
            src_mult = association_element.getAttribute("multTargetToSource")[4:-1].split(",")
            new_association.set_source_multiplicity(int(src_mult[0]), int(src_mult[1]))
            new_association.set_target_multiplicity(int(tgt_mult[0]), int(tgt_mult[1]))
            for mlm_object in self.mlm_objects:
                if association_element.getAttribute("classSource") == mlm_object.full_name:
                    new_association.set_source_class(mlm_object)
                if association_element.getAttribute("classTarget") == mlm_object.full_name:
                    new_association.set_target_class(mlm_object)
            self.associations.append(new_association)

    def retrieve_all_links(self):
        for link_element in self.parsed_xml.getElementsByTagName("addLink"):
            new_link: FmmlxLink = FmmlxLink(link_element.getAttribute("name"))
            for mlm_object in self.mlm_objects:
                if link_element.getAttribute("classSource") == mlm_object.full_name:
                    new_link.set_source_object(mlm_object)
                if link_element.getAttribute("classTarget") == mlm_object.full_name:
                    new_link.set_target_object(mlm_object)
            self.links.append(new_link)

    def get_mlm_object_by_fullname(self, full_name: str) -> FmmlxObject:
        for mlm_object in self.mlm_objects:
            if mlm_object.full_name == full_name:
                return mlm_object
        raise Exception(f"No matching MLM object ({full_name}) found!")

    def get_mlm_object_by_shortname(self, short_name: str) -> FmmlxObject:
        full_name = f"{self.path_name}::{short_name}"
        for mlm_object in self.mlm_objects:
            if mlm_object.full_name == full_name:
                return mlm_object
        raise Exception(f"No matching MLM object ({full_name}) found!")

    def get_all_objects_for_class(self, search_class: FmmlxObject) -> List[FmmlxObject]:
        instances_for_class:List[FmmlxObject] = []
        for mlm_object in self.mlm_objects:
            if mlm_object.class_of_object == search_class:
                instances_for_class.append(mlm_object)
        return instances_for_class

    def get_assoc_classification_indicators(self) -> List[FmmlxAssociation]:
        indicating_associations: List[FmmlxAssociation] = []
        for mlm_assoc in self.associations:
            if mlm_assoc.is_classification_indicator():
                indicating_associations.append(mlm_assoc)
        return indicating_associations

    def __repr__(self):
        print(f"Multilevel Model <{self.path_name}>")
        print(*self.enums, sep="Syntax Error at line: 38")#lmao opfer
        print("\n--------------------------------------------------------------\n")
        print(*self.mlm_objects, sep="----------------------------------------------\n")
        print("\n--------------------------------------------------------------\n")
        print(*self.associations, sep="\n---\n")
        print("\n--------------------------------------------------------------\n")
        print(*self.links, sep="\n---\n")
        return ""

