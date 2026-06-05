from xml.etree.ElementTree import ElementTree

from src.fmmlx_mlm_structure.fm_object import FmmlxObject
from src.fmmlx_mlm_structure.multiplicity import Multiplicity


class FmmlxAssociation:
    def __init__(self, name: str, source_inst_level: int, target_inst_level: int):
        self.name = name
        self.source_inst_level = source_inst_level
        self.target_inst_level = target_inst_level
        self.source_class: FmmlxObject = None
        self.target_class: FmmlxObject = None
        self.source_multiplicity: Multiplicity = None
        self.target_multiplicity: Multiplicity = None

    def set_source_class(self, source_class):
        self.source_class = source_class

    def set_target_class(self, target_class):
        self.target_class = target_class

    def set_source_multiplicity(self, min_card: int, max_card: int):
        # FH java, XMF saves "hasUpperLimit" -> is_unbounded muss genau andersherum sein daher änderung if und else teil
        if max_card == -1:
            self.source_multiplicity = Multiplicity(min_card, max_card, is_unbounded=True)
            # IMPORTANT: DOES NOT WORK IF CONTINGENT ASSOCIATIONS ARE PRESENT
        else:
            self.source_multiplicity = Multiplicity(min_card, max_card)

    def set_target_multiplicity(self, min_card: int, max_card: int):
        # FH java, XMF saves "hasUpperLimit" -> is_unbounded muss genau andersherum sein daher änderung if und else teil
        if max_card == -1:
            self.target_multiplicity = Multiplicity(min_card, max_card, is_unbounded=True)
            # IMPORTANT: DOES NOT WORK IF CONTINGENT ASSOCIATIONS ARE PRESENT
        else:
            self.target_multiplicity = Multiplicity(min_card, max_card)

    def is_classification_indicator(self):
        if self.source_multiplicity.is_exactly_one() and self.target_multiplicity.is_unbounded:
            return True
        else:
            if self.target_multiplicity.is_exactly_one() and self.source_multiplicity.is_unbounded:
                return True
            else:
                return False

    def __repr__(self):
        return (f"[ASSOCIATION {self.name}] {self.source_multiplicity} From {self.source_class.name}"
                f" (at L{self.source_inst_level})"
                f" to {self.target_multiplicity} {self.target_class.name} (at L{self.target_inst_level})")
        # f"\n {self.source_multiplicity} {self.source_class.name}"
        # f" {self.name} {self.target_class.name}")

    def export(self, root: ElementTree.Element):
        projectName = root.attrib['path']
        model = root.find('Model')

        # transform of cardinalities
        multSourceToTarget = 'Seq{' + str(self.target_multiplicity.min_multiplicity) + ',' + str(
            self.target_multiplicity.max_multiplicity) + ',' + str(
            self.target_multiplicity.is_unbounded).lower() + ',false}'

        multTargetToSource = 'Seq{' + str(self.source_multiplicity.min_multiplicity) + ',' + str(
            self.source_multiplicity.max_multiplicity) + ',' + str(
            self.source_multiplicity.is_unbounded).lower() + ',false}'

        # adapt class names to new projectname
        classSourceName = projectName + "::" + self.source_class.name
        targetSourceName = projectName + "::" + self.target_class.name

        # associations use always the class name as an access name at the moment, this leads to a problem when more than one association exists between the same two classes, as the access name is no longer unique
        # TODO think about fix
        addAssoc = ElementTree.SubElement(model, 'addAssociation',
                                          accessSourceFromTargetName=self.source_class.name.lower(),
                                          accessTargetFromSourceName=self.target_class.name.lower(),
                                          associationType='Root::Associations::DefaultAssociation',
                                          classSource=classSourceName, classTarget=targetSourceName, fwName=self.name,
                                          instLevelSource=str(self.source_inst_level),
                                          instLevelTarget=str(self.target_inst_level),
                                          multSourceToTarget=multSourceToTarget, multTargetToSource=multTargetToSource,
                                          package=projectName, reverseName='-1', sourceVisibleFromTarget='false',
                                          targetVisibleFromSource='true')
        return root
