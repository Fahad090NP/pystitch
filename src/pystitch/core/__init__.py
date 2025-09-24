"""Core framework modules"""

from .EmbPattern import EmbPattern
from .EmbConstant import *
from .exceptions import *
# from .pystitch import *  # Removed star import to avoid namespace pollution

__all__ = [
    'EmbPattern',
    # EmbConstant exports
    # Add all symbols exported by EmbConstant here, e.g.:
    # 'SOME_CONSTANT', 'ANOTHER_CONSTANT',
    # exceptions exports
    # Add all symbols exported by exceptions here, e.g.:
    # 'CustomError', 'AnotherException',
    # pystitch exports
    # Add all symbols exported by pystitch here, e.g.:
    # 'stitch_function', 'StitchClass',
]
