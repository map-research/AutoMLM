from enum import EnumMeta
from xml.dom.minidom import parse
from mlm_helper_classes import *

# maybe the import name is confusing
import xml_export as export_xml

metaClass = MlmObject("MetaClass", "MetaClass", "99", None, "false")


# Helper function to parse XML files

# The class MLM serves to represent complete MLM models as provided by an xml file.
# Therefore, it receives a path of the file as an input (parameter "input_source") and parses the file
# All elements of the MLM are then instances of the classes defined in "mlm_helper_classes.py"


class MultilevelModel:

    def __init__(self, xml_file_path: str = ""):
        self.mlm_objects: List[MlmObject] = []
        self.enums: List[EnumType] = []
        self.associations: List[MlmAssociation] = []
        self.links: List[MlmLink] = []
        self.parsed_xml = None
        if xml_file_path != "":
            self._parse_xml(xml_file_path)
        

    def export_xml(self, filepath : str = 'export.xml', project_name='Root::Export'):
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
        if self.parsed_xml is not None:
            raise Exception("Multi-level model is already imported! Overriding of existing model is forbidden.")
        else:
            self._parse_xml(xml_file_path)
            self.extract_mlm_from_xml()

    def extract_mlm_from_xml(self):
        self.mlm_objects = self.retrieve_all_mlm_objects()
        self._set_generalizations()
        self.enums = self.retrieve_all_enums()
        self.retrieve_all_attributes()
        self.retrieve_all_slots()
        self.retrieve_all_operations()
        self.retrieve_all_constraints()
        self.retrieve_all_associations()
        self.retrieve_all_links()

    def retrieve_all_mlm_objects(self) -> List[MlmObject]:
        """
        This operation retrieves all MLM objects/classes. First all highest-level classes are retrieved via the
        function `_retrieve_all_mlm_metaclass_objects.` This is important since they have a separate XML tag.
        Afterward, the remaining MLM objects are retrieved.
        """
        mlm_objects = self._retrieve_metaclass_objects()
        for instance_object in self._retrieve_instance_objects():
            instance_object.set_class_of_object(self._get_class_of_mlm_object(instance_object.class_of_object.full_name,
                                                                              mlm_objects))
            mlm_objects.append(instance_object)
        return mlm_objects

    def _retrieve_metaclass_objects(self) -> List[MlmObject]:
        mlm_objects = []
        for object_element in self.parsed_xml.getElementsByTagName("addMetaClass"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = MlmObject(mlm_object_long, object_element.getAttribute("name"),
                                   object_element.getAttribute("level"), metaClass,
                                   object_element.getAttribute("abstract"))
            mlm_objects.append(mlm_object)

        return mlm_objects

    def _retrieve_instance_objects(self) -> List[MlmObject]:
        mlm_objects = []
        for object_element in self.parsed_xml.getElementsByTagName("addInstance"):
            mlm_object_long = object_element.getAttribute("package") + "::" + object_element.getAttribute("name")
            mlm_object = MlmObject(mlm_object_long, object_element.getAttribute("name"), 99,
                                   MlmObject(object_element.getAttribute("of"),
                                             "", 99, None, "false"),
                                   object_element.getAttribute("abstract"))
            mlm_objects.append(mlm_object)

        return mlm_objects

    def _get_class_of_mlm_object(self, full_object_name: str, mlm_instance_objects: List[MlmObject]) -> MlmObject:
        for object_elem in mlm_instance_objects:
            if object_elem.full_name == full_object_name:
                return object_elem

    def _set_generalizations(self):
        for parent_element in self.parsed_xml.getElementsByTagName("changeParent"):
            child_class: MlmObject = self.get_mlm_object_by_fullname(parent_element.getAttribute("class"))
            for parent_class_name in parent_element.getAttribute("new").split(","):
                child_class.add_parent_class(self.get_mlm_object_by_fullname(parent_class_name))

    def retrieve_all_enums(self):
        enums_tmp: List[EnumType] = []
        for enum_element in self.parsed_xml.getElementsByTagName("addEnumeration"):
            enums_tmp.append(EnumType(enum_element.getAttribute("name")))
        for enum_value_element in self.parsed_xml.getElementsByTagName("addEnumerationValue"):
            for enum_tmp in enums_tmp:
                if enum_value_element.getAttribute("enum_name") == enum_tmp.enum_name:
                    enum_tmp.add_enum_value(enum_value_element.getAttribute("enum_value_name"))
        return enums_tmp

    def retrieve_all_attributes(self):
        for attribute_element in self.parsed_xml.getElementsByTagName("addAttribute"):
            new_attr = MlmAttr(attribute_element.getAttribute("name"), attribute_element.getAttribute("type"),
                               attribute_element.getAttribute("level"))
            # need to look for custom attr data types: enums or custom class types
            if new_attr.attr_type.split("::")[1] != "XCore" and new_attr.attr_type.split("::")[1] != "Auxiliary":
                if not self._is_custom_attribute_type_an_enum(new_attr):
                    print("CUSTOM CLASS") #TODO CUSTOM CLASS AS OBJECT
            for mlm_object in self.mlm_objects:
                if attribute_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_attr(new_attr)

    def _is_custom_attribute_type_an_enum(self, mlm_attr: MlmAttr) -> bool:
        # check 1: look if in list of enums
        for enum in self.enums:
            if enum.enum_name == mlm_attr.attr_type_short:
                mlm_attr.set_enum_type(enum)
                return True
        return False

    def retrieve_all_slots(self):
        for slot_element in self.parsed_xml.getElementsByTagName("changeSlotValue"):
            new_slot = MlmSlot(slot_element.getAttribute("slotName"), slot_element.getAttribute("valueToBeParsed"))
            for mlm_object in self.mlm_objects:
                if slot_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_slot(new_slot)

    def retrieve_all_operations(self):
        for operations_element in self.parsed_xml.getElementsByTagName("addOperation"):
            new_operation = MlmOperation(operations_element.getAttribute("name"),
                                         operations_element.getAttribute("level"),
                                         operations_element.getAttribute("type"))

            for mlm_object in self.mlm_objects:
                if operations_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_operation(new_operation)

    def retrieve_all_constraints(self):
        for constraint_element in self.parsed_xml.getElementsByTagName("addConstraint"):
            new_constraint = MlmConstraint(constraint_element.getAttribute("constName"),
                                           constraint_element.getAttribute("instLevel"))
            for mlm_object in self.mlm_objects:
                if constraint_element.getAttribute("class") == mlm_object.full_name:
                    mlm_object.add_constraint(new_constraint)

    def retrieve_all_associations(self):
        for association_element in self.parsed_xml.getElementsByTagName("addAssociation"):
            new_association = MlmAssociation(association_element.getAttribute("fwName"),
                                             association_element.getAttribute("instLevelSource"),
                                             association_element.getAttribute("instLevelTarget"))
            src_mult = association_element.getAttribute("multSourceToTarget")[4:-1].split(",")
            tgt_mult = association_element.getAttribute("multTargetToSource")[4:-1].split(",")
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
            new_link: MlmLink = MlmLink(link_element.getAttribute("name"))
            for mlm_object in self.mlm_objects:
                if link_element.getAttribute("classSource") == mlm_object.full_name:
                    new_link.set_source_object(mlm_object)
                if link_element.getAttribute("classTarget") == mlm_object.full_name:
                    new_link.set_target_object(mlm_object)
            self.links.append(new_link)


    def get_mlm_object_by_fullname(self, full_name: str) -> MlmObject:
        for mlm_object in self.mlm_objects:
            if mlm_object.full_name == full_name:
                return mlm_object
        raise Exception(f"No matching MLM object ({full_name}) found!")

    def __repr__(self):
        print(*self.enums, sep="\n---\n")
        print("\n--------------------------------------------------------------\n")
        print(*self.mlm_objects, sep="----------------------------------------------\n")
        print("\n--------------------------------------------------------------\n")
        print(*self.associations, sep="\n---\n")
        print("\n--------------------------------------------------------------\n")
        print(*self.links, sep="\n---\n")
        return ""
