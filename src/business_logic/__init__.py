"""
Logika biznesowa systemu SPA
"""
from .validators import QualificationValidator
from .prioritizer import DealPrioritizer
from .allocator import SlotAllocator
from .promoter import DealPromoter

__all__ = [
    "QualificationValidator",
    "DealPrioritizer",
    "SlotAllocator",
    "DealPromoter",
]

