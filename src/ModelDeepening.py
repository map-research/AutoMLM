class ModelDeepening:

    # init only accepts single MLM file currently, may be expanded to multiple files in the future
    def __init__(self, input_model: MultiLevelModel = None):
        self.original_model: MultiLevelModel = input_model
        self.output_model: MultiLevelModel = input_model

    def set_input_model(self, input_model: MultiLevelModel):
        assert self.original_model is None, "Original model already specified"
        self.original_model: MultiLevelModel = input_model
        self.output_model: MultiLevelModel = input_model

    def get_original_model(self) -> MultiLevelModel:
        return self.original_model

    def get_output_model(self) -> MultiLevelModel:
        return self.output_model

    def set_output_model(self, output_model: MultiLevelModel):
        self.output_model = output_model

    def export_multi_level_model_as_xmf(self):
        assert self.output_model is not None, "No output model is specified"
        self.output_model.export_xml()
