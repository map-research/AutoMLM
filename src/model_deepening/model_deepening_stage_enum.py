from enum import Enum


class ModelDeepeningStage(Enum):
    """This enumeration is used to determine the stage of a model-deepening workflow
    If in original, the input model has not been changed yet."""
    ORIGINAL = "Original"
    CHANGED = "Changed"
    FINAL = "Final"
