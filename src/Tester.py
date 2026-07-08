from src.ModelDeepening import ModelDeepening


# class Tester is currently dummy class, serves as a shell for more specific Tester classes
class Tester:

    def __init__(self, input_file_sub_path: str = "", file_name: str = ""):
        self.test_name: str = "Name of Test"
        self.files_base_path: str = "C:\\Users\\PierreM\\git\\MosaicFX\\AutoMLM\\mlm_files\\"
        self.input_file_sub_path: str = input_file_sub_path
        self.input_file_folder_path: str = self.files_base_path + self.input_file_sub_path
        self.file_name: str = ""
        self.complete_path: str = self.input_file_folder_path + self.file_name
        self.md_instance: ModelDeepening = ModelDeepening()

    def set_file_name(self, file_name: str):
        self.file_name = file_name
        self.update_path()

    def set_input_file_sub_path(self, input_file_sub_path: str):
        self.input_file_sub_path = input_file_sub_path
        self.update_path()

    def update_path(self):
        self.input_file_folder_path = self.files_base_path + self.input_file_sub_path
        self.complete_path = self.input_file_folder_path + self.file_name

    def get_original_model_path(self):
        return self.complete_path

    def get_md_instance(self):
        return self.md_instance
