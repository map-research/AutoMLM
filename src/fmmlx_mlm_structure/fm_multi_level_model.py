from enum import EnumMeta
from xml.dom.minidom import parse
from src.fmmlx_mlm_structure import xml_export as export_xml

from typing import List, Optional
import csv
import keyword #für reservierten Wert
import os #für Dateinamen aus Dateiendung
import re #für Prüfung von Zeichen

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

    def __init__(self, file_path: str = "", print_progress: bool = False, selected_csv_columns: Optional[List[str]] = None):
        self.path_name = ""
        self.mlm_objects: List[FmmlxObject] = []
        self.enums: List[FmmlxEnumType] = []
        self.associations: List[FmmlxAssociation] = []
        self.links: List[FmmlxLink] = []
        self.parsed_xml = None
        self.print_progress = print_progress
        if file_path != "":
            # Der Parameter heisst noch xml_file_path, weil er frueher nur fuer XML gedacht war.
            # Inzwischen darf hier aber auch ein CSV-Pfad stehen.
            # Die Dateiendung entscheidet, wie die Datei gelesen wird.
            file_extension = os.path.splitext(file_path)[1].lower() #[1] für Dateiende
            if file_extension == ".csv":
                self._import_csv(file_path, selected_csv_columns)
            elif file_extension == ".xml":
                self._parse_xml(file_path)
            else:
                raise ValueError(f"File '{file_path}' must be a CSV or XML file.")

    def _import_csv(self, csv_file_path: str, selected_csv_columns: Optional[List[str]] = None):
        """
        import CSV as MultiLevelModel. Note that CSV imports only account for classes and objects; relationships
        between classes and objects are not accounted for.
        """
        all_mlm_objects: List[FmmlxObject] = []
        # CSV files can contain special characters such as umlauts or non-English names.
        # On Windows, open() may otherwise use the local default encoding and fail while reading.
        # utf-8-sig reads normal UTF-8 files and also ignores a possible BOM marker from Excel.
        with open(csv_file_path, "r", newline="", encoding="utf-8-sig") as csv_file: #r = read
            # Das Trennzeichen wird erkannt, damit auch Dateien mit ; oder Tab funktionieren.
            csv_reader = csv.reader(csv_file, self._get_csv_dialect(csv_file), skipinitialspace=True)
            #mit strip vorne und hinten Leerzeichen und Anführungszeichen entfernen
            rows = [[value.strip().strip("\"") for value in row] for row in csv_reader if row]

        # prüft, dass Datei nicht leer ist
        assert len(rows) > 0, "CSV file must contain at least one row."

        # Die erste Zeile beschreibt die Spalten. Die restlichen Zeilen sind die Daten.
        header_row = rows[0]
        data_rows = rows[1:]
        number_of_columns = len(header_row)
        # prüft, dass erste Zele mindestens eine Spalte hat
        assert number_of_columns > 0, "CSV header must contain at least one column."
        # prüft, ob erste Zeile wirklich Schema-Infos enthält
        assert self._first_row_looks_like_header(header_row, data_rows), (
            "CSV header does not look valid. The first row seems to contain data instead of attribute names."
        )

        # Jede Datenzeile muss genauso viele Werte haben wie die erste Zeile (daher start bei 2)
        for row_number, row in enumerate(data_rows, start=2):
            assert len(row) == number_of_columns, (
                f"CSV row {row_number} has {len(row)} values, but the header has {number_of_columns} values."
            )

        if selected_csv_columns is not None:
            # The user can list the columns that should become attributes in the model.
            header_row, data_rows = self._select_csv_columns(header_row, data_rows, selected_csv_columns)
            number_of_columns = len(header_row)

        # Der Klassenname kommt aus dem Dateinamen.
        class_name = self._make_csv_class_name(csv_file_path)
        project_name = f"Root::{class_name}"
        self.path_name = project_name

        # Hier wird die eine Klasse gebaut, zu der alle CSV-Zeilen später gehören.
        # Beispiel: Aus der Datei news_decline.csv wird die Klasse NewsDecline.
        mlm_class: FmmlxObject = FmmlxObject(
            f"{project_name}::{class_name}", class_name, "1", FmmlxObject.meta_class(), "false"
        )
        all_mlm_objects.append(mlm_class) #speichert Klasse im Modell

        all_csv_attr = []
        used_attribute_names = []
        for col_counter, raw_attribute_name in enumerate(header_row):
            # Aus jeder Spalte wird ein Attribut.
            attribute_name = self._make_safe_name(raw_attribute_name, "attribute", allow_first_char_digit=True)
            attribute_name = self._make_unique_name(attribute_name, used_attribute_names) #für doppelte Namen
            column_values = [row[col_counter] for row in data_rows] #holt alle Werte dieser Spalte
            attribute_type = self._get_csv_attribute_type(column_values) #String, Integer oder Float
            new_attr: FmmlxAttribute = FmmlxAttribute(attribute_name, attribute_type, 0)
            new_attr.set_owner(mlm_class)
            all_csv_attr.append(new_attr) #attribut in Liste
            mlm_class.add_attr(new_attr) #fügt zur Klasse hinzu

        for row_counter, row in enumerate(data_rows, start=1):
            # Aus jeder Datenzeile wird eine Instanz mit eindeutigem Namen.
            instance_name = f"{class_name.lower()}{row_counter}"
            mlm_instance: FmmlxObject = FmmlxObject(
                f"{project_name}::{instance_name}", instance_name, "0", mlm_class, "false"
            )
            mlm_class.add_instance(mlm_instance)
            all_mlm_objects.append(mlm_instance)

            #Slots einfügen
            for col_counter, value in enumerate(row):
                attribute = all_csv_attr[col_counter]
                new_slot: FmmlxSlot = FmmlxSlot(attribute.attr_name, self._convert_csv_value(value, attribute.attr_type))
                new_slot.set_owner_object(mlm_instance)
                # Der Slot bekommt direkt das Attribut aus seiner Spalte.
                new_slot.set_attribute(attribute)
                mlm_instance.add_slot(new_slot)

        self._set_mlm_objects(all_mlm_objects)

    # Ab hier kommen kleine Hilfsfunktionen, um den Import oben kuerzer zu halten.
    def _get_csv_dialect(self, csv_file):
        # Es wird nur ein kleiner Anfang der Datei angeschaut, per Default "," .
        sample = csv_file.read(2048)
        csv_file.seek(0)
        try:
            return csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            # csv.Sniffer can fail when the first rows contain many empty cells or irregular values.
            # Returning csv.excel directly would use "," as delimiter, which breaks semicolon CSV files.
            # Therefore, we count the allowed delimiters in the sample and use the one that appears most often.
            dialect = csv.excel
            delimiter_counts = {delimiter: sample.count(delimiter) for delimiter in [",", ";", "\t", "|"]}
            dialect.delimiter = max(delimiter_counts, key=delimiter_counts.get)
            return dialect

    def _select_csv_columns(self, header_row: List[str], data_rows: List[List[str]],
                            selected_csv_columns: List[str]):
        # Without at least one selected column, the CSV class would not have any attributes.
        assert len(selected_csv_columns) > 0, "At least one CSV column must be selected."

        selected_column_numbers = []
        missing_column_names = []
        for selected_column in selected_csv_columns:
            # For every selected column name, we search the matching position in the CSV header.
            matching_column_number = self._get_csv_column_number(header_row, selected_column)
            if matching_column_number is None:
                # Missing names are collected first, so the error can show all wrong column names at once.
                missing_column_names.append(selected_column)
            else:
                # We store the column number because the data rows are selected by position later.
                selected_column_numbers.append(matching_column_number)

        assert not missing_column_names, f"Selected CSV columns were not found: {missing_column_names}"

        # The header is reduced to the selected columns, so only these columns become attributes.
        selected_header_row = [header_row[col_number] for col_number in selected_column_numbers]
        # Every data row is reduced in the same order, so the slots still match the selected attributes.
        selected_data_rows = [
            [row[col_number] for col_number in selected_column_numbers]
            for row in data_rows
        ]
        return selected_header_row, selected_data_rows

    def _get_csv_column_number(self, header_row: List[str], selected_column: str):
        for col_counter, raw_header_name in enumerate(header_row):
            # The user may enter the original CSV name or the safe attribute name used in the model.
            safe_header_name = self._make_safe_name(raw_header_name, "attribute", allow_first_char_digit=True)
            if selected_column == raw_header_name or selected_column == safe_header_name:
                return col_counter
        # None means that this selected column does not exist in the CSV header.
        return None

    #Wenn es keine Daten gibt, kann man nicht vergleichen. Dann wird die Kopfzeile akzeptiert.
    def _first_row_looks_like_header(self, header_row: List[str], data_rows: List[List[str]]) -> bool:
        if len(data_rows) == 0:
            return True

        # Namen wie "name" oder "city" sind als erste Zeile in Ordnung.
        if all(self._is_simple_header_name(header_value) for header_value in header_row):
            return True

        # Wenn die erste Zeile wie normale Daten aussieht, ist sie wahrscheinlich keine Kopfzeile.
        for col_counter, header_value in enumerate(header_row):
            column_values = [row[col_counter] for row in data_rows]
            if self._get_simple_csv_value_type(header_value) not in self._get_simple_csv_column_types(column_values): #also wenn erste Zeile anders aussieht als die Daten dadrunter, ist es wahrsheinlich ein Header
                return True
        return False

    def _is_simple_header_name(self, value: str) -> bool:
        return re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) is not None

    def _get_simple_csv_column_types(self, values: List[str]) -> List[str]:
        column_types = []
        for value in values:
            value_type = self._get_simple_csv_value_type(value)
            if value_type not in column_types:
                column_types.append(value_type)
        return column_types

    def _get_simple_csv_value_type(self, value: str) -> str:
        if value == "":
            return "empty"
        if self._is_integer(value):
            return "integer"
        if self._is_float(value):
            return "float"
        return "string"

    def _make_csv_class_name(self, csv_file_path: str) -> str:
        # Aus "news_decline.csv" wird zum Beispiel "NewsDecline".
        file_name = os.path.splitext(os.path.basename(csv_file_path))[0]
        safe_name = self._make_safe_name(file_name, "CsvClass")
        return "".join(name_part.capitalize() for name_part in safe_name.split("_"))

    def _make_safe_name(self, name: str, fallback_name: str, allow_first_char_digit: bool = False) -> str:
        # Zeichen, die in Namen stören können, werden durch _ ersetzt.
        safe_name = re.sub(r"\W", "_", name.strip())
        safe_name = re.sub(r"_+", "_", safe_name).strip("_")
        if safe_name == "":
            safe_name = fallback_name
        if safe_name[0].isdigit() and not allow_first_char_digit:
            safe_name = f"{fallback_name}_{safe_name}"
        if keyword.iskeyword(safe_name):
            safe_name = f"{safe_name}_{fallback_name}"
        return safe_name

    def _make_unique_name(self, name: str, already_used_names: List[str]) -> str:
        # Gleiche Namen bekommen eine Zahl am Ende.
        unique_name = name
        number = 2
        while unique_name in already_used_names:
            unique_name = f"{name}_{number}"
            number += 1
        already_used_names.append(unique_name)
        return unique_name

    def _get_csv_attribute_type(self, values: List[str]) -> str:
        # Wenn alle Werte Zahlen sind, wird auch das Attribut als Zahl gespeichert.
        values_without_empty_strings = [value for value in values if value != ""]
        if values_without_empty_strings and all(self._is_integer(value) for value in values_without_empty_strings):
            return "Root::XCore::Integer"
        if values_without_empty_strings and all(self._is_float(value) for value in values_without_empty_strings):
            return "Root::XCore::Float"
        return "Root::XCore::String"

    def _convert_csv_value(self, value: str, attribute_type: str):
        # Der Wert wird passend zum erkannten Attribut gespeichert.
        if value == "":
            return value
        if attribute_type == "Root::XCore::Integer":
            return int(value)
        if attribute_type == "Root::XCore::Float":
            return float(value)
        return value

    def _is_integer(self, value: str) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _is_float(self, value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    # Ab hier gehen die normalen Funktionen weiter.
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
        return cls(file_path=loc)

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
