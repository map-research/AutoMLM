from typing import List
from xml.dom.minidom import parse
from mlm_classes import *

metaClass = MlmObject("MetaClass", "MetaClass", 99, [], [], object())
instanceDummy = MlmObject("Dummy", "Dummy", 555, [], [], object())


class MlmDoc:
    def __init__(self, input_source):
        self.xml_document = input_source
        self.mlm_objects = self.retrieve_all_mlm_objects(self._parse_xml(input_source))

    @classmethod
    def input(cls):
        print("BEGIN MLM EXTRACTION\nEnter the MLM Source Location:")
        loc = input()
        return cls(loc)

    def _parse_xml(self, source_location):
        document = None
        try:
            document = parse(source_location)
        except FileNotFoundError:
            print(f"\nFile '{source_location}' was not found!")
        except:
            print(f"\nFile '{source_location}' is no XML document")

        assert document.documentElement.tagName == "XModeler", "File is no Multi-Level Model!"

        return document

    def retrieve_all_mlm_objects(self, mlm_document) -> List[MlmObject]:
        mlm_objects = self._retrieve_metaclass_objects(mlm_document)
        for instance_object in self._retrieve_instance_objects(mlm_document):
            instance_object.set_super_object(self.get_parent_mlm_object(mlm_document, instance_object.super_object.full_name,
                                                                   mlm_objects))
            mlm_objects.append(instance_object)
        return mlm_objects

    def _retrieve_metaclass_objects(self, mlm_document) -> List[MlmObject]:
        mlm_objects = []
        for object_element in mlm_document.getElementsByTagName("addMetaClass"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = MlmObject(mlm_object_long, object_element.getAttribute("name"),
                                   object_element.getAttribute("level"),
                                   self.retrieve_attributes_for_mlm_object(mlm_document, mlm_object_long),
                                   self.retrieve_slots_for_mlm_object(mlm_document, mlm_object_long), #impossible
                                   metaClass)
            mlm_objects.append(mlm_object)

        return mlm_objects

    def _retrieve_instance_objects(self, mlm_document) -> List[MlmObject]:
        mlm_objects = []
        for object_element in mlm_document.getElementsByTagName("addInstance"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = MlmObject(mlm_object_long, object_element.getAttribute("name"), 99,
                                   self.retrieve_attributes_for_mlm_object(mlm_document, mlm_object_long),
                                   self.retrieve_slots_for_mlm_object(mlm_document, mlm_object_long),
                                   MlmObject(object_element.getAttribute("of"), "", 99, [], [], object()))
            mlm_objects.append(mlm_object)

        return mlm_objects

    def get_parent_mlm_object(self, xml_document, full_object_name: str, mlm_objects: List[MlmObject]) -> MlmObject:
        for object_elem in mlm_objects:
            if object_elem.full_name == full_object_name:
                return object_elem

    def retrieve_attributes_for_mlm_object(self, xml_document, full_object_name: str) -> List[MlmAttr]:
        mlm_attr_list = []
        for attr_elem in xml_document.getElementsByTagName("addAttribute"):
            if attr_elem.getAttribute("class") == full_object_name:
                mlm_attr = MlmAttr(attr_elem.getAttribute("name"), attr_elem.getAttribute("type"),
                                   attr_elem.getAttribute("level"))
                mlm_attr_list.append(mlm_attr)
        return mlm_attr_list

    def retrieve_slots_for_mlm_object(self, mlm_doc, full_object_name: str) -> List[MlmSlot]:
        mlm_slot_list = []
        for slot_elem in mlm_doc.getElementsByTagName("changeSlotValue"):
            if slot_elem.getAttribute("class") == full_object_name:
                mlm_slot = MlmSlot(MlmAttr("test", "test::test::test", 3), slot_elem.getAttribute("valueToBeParsed"))
                mlm_slot_list.append(mlm_slot)
        return mlm_slot_list

    def __repr__(self):
        print(*self.mlm_objects, sep="----------------------------------------------\n")
        return ""


