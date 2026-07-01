from src.fmmlx_mlm_structure.fm_multi_level_model import FmmlxModel

selected_columns = ["brand_name", "model", "price"]
my_model: FmmlxModel = FmmlxModel(file_path="csv_files/smartphone.csv", selected_csv_columns=selected_columns)

print("L1 classes:")
print(*my_model.get_all_flat_classes(), sep="\n")

print("First L0 objects:")
print(*my_model.get_all_pure_objects()[:3], sep="\n")
