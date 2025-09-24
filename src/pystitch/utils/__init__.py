"""Utility modules"""

# from .EmbFunctions import *  # type: ignore
from .EmbMatrix import EmbMatrix  # type: ignore
# from .EmbEncoder import *  # type: ignore
from .EmbCompress import compress, expand  # type: ignore
# from .ReadHelper import *  # type: ignore
# from .WriteHelper import *  # type: ignore
# from .GenericWriter import *  # type: ignore
from .PecGraphics import get_graphic_as_string  # type: ignore

# Aggregate __all__ from all star-imported submodules
from . import EmbFunctions, EmbEncoder, ReadHelper, WriteHelper, GenericWriter
__all__ = (
    list(getattr(EmbFunctions, '__all__', [])) +
    list(getattr(EmbEncoder, '__all__', [])) +
    list(getattr(ReadHelper, '__all__', [])) +
    list(getattr(WriteHelper, '__all__', [])) +
    list(getattr(GenericWriter, '__all__', [])) +
    ['EmbMatrix', 'compress', 'expand', 'get_graphic_as_string']
)
