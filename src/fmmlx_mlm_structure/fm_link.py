from xml.etree.ElementTree import ElementTree

from fmmlx_mlm_structure.model_element import ModelElement
from src.fmmlx_mlm_structure.fm_association import FmmlxAssociation
from src.fmmlx_mlm_structure.fm_object import FmmlxObject


class FmmlxLink(ModelElement):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.source_object: FmmlxObject = None
        self.target_object: FmmlxObject = None
        self.association: FmmlxAssociation = None

    def export(self, root):
        projectName = root.attrib['path']
        model = root.find('Model')
        addLink = ElementTree.SubElement(model, 'addLink', classSource=self.source_object.full_name, classTarget=self.target_object.full_name, name=self.name, package=projectName)
        return root

    def set_source_object(self, source_object: FmmlxObject):
        self.source_object = source_object

    def set_target_object(self, target_object: FmmlxObject):
        self.target_object = target_object

    def get_source_object(self) -> FmmlxObject:
        return self.source_object

    def get_target_object(self) -> FmmlxObject:
        return self.target_object

    def get_association(self) -> FmmlxAssociation:
        return self.association

    def set_association(self, association: FmmlxAssociation):
        self.association = association

    def __repr__(self):
        return f"[LINK {self.name}] From {self.source_object.object_name} to {self.target_object.object_name}"