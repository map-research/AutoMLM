class FmmlxConstraint:

    def __init__(self, constraint_name: str, inst_level: int):
        self.constraint_name = constraint_name
        self.inst_level = inst_level

    def __repr__(self):
        return f"[CONST-{self.inst_level}] {self.constraint_name}"
