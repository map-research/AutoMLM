from src.precedence_analysis_tester import PrecedenceAnalysisTester
from src.fmmlx_mlm_structure.fm_multi_level_model import FmmlxModel


pa_tester = PrecedenceAnalysisTester(variant=6,
                                     print_input_model=False,
                                     track_progress=False,
                                     export_precedence_graphs_as_png=True,
                                     print_precedence_graph=True)
