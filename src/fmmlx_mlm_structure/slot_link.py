from src.fmmlx_mlm_structure.fm_link import FmmlxLink
from src.fmmlx_mlm_structure.fm_slot import FmmlxSlot


class FmmlxSlotLink(FmmlxSlot):

    def __init__(self, slot_name: str, value: str, link: FmmlxLink, is_source_end: bool):
        """The value of a SlotLink is always the full name of an existing object,
        allowing to retrieve it within the context of a model"""
        super().__init__(slot_name, value.split("::")[2])
        # value only returns short name of object, may lead to problems if name is reused in other slots
        self.slot_category = "SLOT-LINK"
        self.link = link
        self.is_source_end = is_source_end

    def get_link(self) -> FmmlxLink:
        return self.link

    def set_link(self, link: FmmlxLink):
        self.link = link

    def get_attribute(self):
        if self.is_source_end:
            return self.link.get_association().get_source_association_end()
        else:
            return self.link.get_association().get_target_association_end()