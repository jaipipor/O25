"""Internal BH4 functionality."""

from .classifier import ClassResult, assign_class
from .features import FeatureResult, features_from_rrs
from .lookup import (
    GEOMETRY_TOLERANCE_DEG,
    ExactLookupResult,
    GeometryNotFoundError,
    canonical_geometry,
    exact_node_lookup,
)
from .model import BH4Classifier, BH4Model, BH4ModelError, load_model

__all__ = [
    "BH4Classifier", "BH4Model", "BH4ModelError", "ClassResult",
    "ExactLookupResult", "FeatureResult", "GEOMETRY_TOLERANCE_DEG",
    "GeometryNotFoundError", "assign_class", "canonical_geometry",
    "exact_node_lookup", "features_from_rrs", "load_model",
]
