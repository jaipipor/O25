"""O25 bidirectional correction with automatic BH4 uncertainty."""
from importlib.metadata import PackageNotFoundError, version
from .api import O25Result, correct
from .model import O25Model
from .O25_hyp import O25_hyp
try:
    __version__ = version("o25")
except PackageNotFoundError:
    __version__ = "0+unknown"
__all__ = ["correct", "O25Model", "O25Result", "O25_hyp", "__version__"]
