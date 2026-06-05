class FmmlxOperation:
    def __init__(self, operation_name: str, inst_level: int, return_type: str):
        self.operation_name = operation_name
        self.inst_level = inst_level
        self.return_type = return_type

    def __repr__(self):
        return f"[OP-{self.inst_level}] {self.operation_name}():{self.return_type}"