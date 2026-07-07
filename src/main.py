from src.precedence_analysis_tester import PrecedenceAnalysisTester
from src.fmmlx_mlm_structure.fm_multi_level_model import FmmlxModel


pa_tester = PrecedenceAnalysisTester(variant=6,
                                     print_input_model=True,
                                     track_progress=True,
                                     export_precedence_graphs_as_png=False,
                                     print_precedence_graph=True)
