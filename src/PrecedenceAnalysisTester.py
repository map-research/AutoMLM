from src.Tester import Tester
from src.fmmlx_mlm_structure.fm_multi_level_model import FmmlxModel


class PrecedenceAnalysisTester(Tester):
    def __init__(self, variant: int = 1, print_input_model: bool = False, export_model: bool = False):
        super().__init__()
        self.set_input_file_sub_path("prop-precedence\\")
        self.variant: int = variant
        self.print_input_model: bool = print_input_model
        self.export_model: bool = export_model
        self.init_simple_precedence_test()

    def init_simple_precedence_test(self):
        match self.variant:
            case 1:
                self.init_simple_car_test()
            case _:
                raise Exception("Invalid test variant (variant number: " + str(self.variant) + ") specified")
        if self.export_model:
            self.export_model_xml()

    def init_simple_car_test(self):
        self.set_file_name("MD_CarSimple.xml")
        self.get_md_instance().set_input_model(FmmlxModel(self.get_original_model_path()))
        if self.print_input_model:
            print(self.get_md_instance().get_original_model())

    def export_model_xml(self):
        self.get_md_instance().export_multi_level_model_as_xmf()
