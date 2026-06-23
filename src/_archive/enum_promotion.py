from enum import Enum


class AutomationTechnique (Enum):
    LEXICAL_DB = 1
    FCA = 2
    CLUSTERING = 3
    CLASSIFICATION = 4
    LLM = 5


class PromotionCase (Enum):
    GEN_1 = 1
