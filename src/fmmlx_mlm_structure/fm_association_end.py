from src.fmmlx_mlm_structure.fm_association import FmmlxAssociation
from src.fmmlx_mlm_structure.fm_attr import FmmlxAttribute


class FmmlxAssociationEnd(FmmlxAttribute):
    def __init__(self, attr_name: str, attr_type: str, inst_level: int, association: FmmlxAssociation,
                 is_source_end: bool):
        """The type of an association name is not the domain-specific type but instead the unique full object name,
        allowing to retrieve the object if required."""
        super().__init__(attr_name, attr_type, inst_level, False, True)
        self.attr_category = "ASSOC-END"
        self.association = association
        self.is_source_end = is_source_end

    def get_association(self) -> FmmlxAssociation:
        return self.association

    def set_association(self, association: FmmlxAssociation):
        self.association = association
