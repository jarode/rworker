"""
Modele danych dla systemu SPA
"""
from .enums import (
    DealStage,
    SPAStage,
    Gender,
    Housing,
    DealPriority,
    GenderlessOrder,
    YesNo,
    SPAPriorityType,
    GENDER_LABELS,
    HOUSING_LABELS,
    PRIORITY_LABELS,
    STAGE_LABELS,
    get_category_key,
)
from .spa import SPA
from .deal import Deal

__all__ = [
    # Enumy
    "DealStage",
    "SPAStage",
    "Gender",
    "Housing",
    "DealPriority",
    "GenderlessOrder",
    "YesNo",
    "SPAPriorityType",
    # Labele
    "GENDER_LABELS",
    "HOUSING_LABELS",
    "PRIORITY_LABELS",
    "STAGE_LABELS",
    # Funkcje pomocnicze
    "get_category_key",
    # Modele
    "SPA",
    "Deal",
]

