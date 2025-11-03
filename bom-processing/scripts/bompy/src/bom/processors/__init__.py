"""Data processors for converting raw data to PostgreSQL-ready records."""

from .bills import BillsProcessor
from .christenings import ChristeningsProcessor
from .christenings_gender import ChristeningsGenderProcessor
from .christenings_parish import ChristeningsParishProcessor
from .foodstuffs import FoodstuffsProcessor

__all__ = [
    "BillsProcessor",
    "FoodstuffsProcessor",
    "ChristeningsProcessor",
    "ChristeningsGenderProcessor",
    "ChristeningsParishProcessor",
]
