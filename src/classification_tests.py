from src.MultiLevelModelAnalyzer import MultiLevelModelAnalyzer
from src.mlm_class import MultilevelModel
from src.mlm_helper_classes import MlmObject, MlmAssociation
from itertools import chain

#uf_product_model = MultilevelModel('C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\datenmodell.xml')

"""
def run_ci_analysis(flat_model: MultilevelModel):
    assoc_indicators = flat_model.get_assoc_classification_indicators()
    for assoc in assoc_indicators:
        if assoc.source_multiplicity.is_exactly_one():
            print(f"{assoc.source_class.name} may be promoted")
        if assoc.target_multiplicity.is_exactly_one():
            print(f"{assoc.target_class.name} may be promoted")
"""
def airplane_example():
    flight_model = MultilevelModel('C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\FlightManagement.xml',
                                   print_progress=False)
    airplane: MlmObject = flight_model.get_mlm_object_by_shortname("Airplane")

    # print(airplane)
    # print(*flight_model.get_all_objects_for_class(airplane))
    mlm_analyzer = MultiLevelModelAnalyzer(flight_model)
    mlm_analyzer.analyze_attribute_precedence_for_class(airplane)

def car_example():
    car_model = MultilevelModel('C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\MD_CarComplex.xml',
                                print_progress=False)
    car_class: MlmObject = car_model.get_mlm_object_by_shortname("RentalCar")

    mlm_analyzer = MultiLevelModelAnalyzer(car_model)
    mlm_analyzer.construct_attribute_codependency_graph(car_class)

def oc_example():
    oc_example_model_small = MultilevelModel("C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\mlm_files"
                                             "\\standard-oc-small.xml", print_progress=False)
    mlm_analyzer = MultiLevelModelAnalyzer(oc_example_model_small)
    for i, flat_class in enumerate(oc_example_model_small.get_all_flat_classes(), start=0):
        print(f"------------------------------------------------------------------------------------------------\n"
              f"ANLYZING ATTRIBUTE CO-DEPENDENCY FOR CLASS <{flat_class.name}>\n")
        mlm_analyzer.analyze_attribute_precedence_for_class(flat_class)


def custom_example(path_to_standard_fmmlx: str, all_classes: bool, single_class_name: str = "", is_csv: bool = False):
    if is_csv:
        example_model = MultilevelModel(csv_file_path=path_to_standard_fmmlx)
    else:
        example_model = MultilevelModel(path_to_standard_fmmlx)
    mlm_analyzer = MultiLevelModelAnalyzer(example_model)
    mlm_analyzer.model_deepening(all_classes, single_class_name=single_class_name)


def run_llm_example():
    all_classes: bool = False
    single_class_name: str = ""
    path_to_standard_fmmlx: str = ""
    print("-------------------------------------------------------------------------------------------------\n"
          "CO-DEPENDENCY ANALYSIS INITIATED\n")

    print("Remember to provide only FLAT STANDARD FMMLX models which contain at least two "
          "instances for all classes you want to analyze.\n")

    print("Please provide the path to the standard FMMLx model you want to analyze:")
    path_to_standard_fmmlx = input()

    print("Do you want to analyze all classes in the model? (Enter 'y' for yes, 'n' for no)")
    if input().lower() == "y":
        all_classes = True

    if not all_classes:
        print("Please provide the name of the class you want to analyze (avoid typos):")
        single_class_name = input()

    custom_example(path_to_standard_fmmlx, all_classes, single_class_name)

# FOR VICKY:: use this file to run co-dependency analysis experiments, remember to use Standard FMMLx

# if you remove the hastag below and execute this file, the airplane example will be executed with the
# four example instances I also provided to you

#airplane_example()

# you can run the airplane example by entering the path to the model and entering "Airplane" as the class name afterwards
# (in this directory, the model is located in "mlm_files")

#run_llm_example()

#car_example()

oc_small = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\mlm_files\\standard-oc-small.xml"
car_simple = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\MD_CarSimple.xml"
car_simple_v2 = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\MD_CarSimple-cr.xml"
car_simple_v3 = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\MD_CarSimple_v3.xml"
car_simple_v4 = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\CarSimple-v4.xml"
car_simple_v5 = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\CarSimple-v5.xml"
car = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\MD_CarComplex.xml"
csv_model = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\csv_files\\news_decline.csv"



print(MultilevelModel(car_simple_v5))
#custom_example(car_simple_v5, True)

