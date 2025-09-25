"""Thread management modules"""

from .EmbThread import *
from .EmbThreadHus import *
from .EmbThreadJef import *
from .EmbThreadPec import *
from .EmbThreadSew import *
from .EmbThreadShv import *

# Explicit __all__ aggregation to avoid type checker warnings
__all__ = [
    # EmbThread exports
    'EmbThread', 'build_unique_palette', 'build_palette', 'build_nonrepeat_palette',
    'find_nearest_color_index', 'color_distance_red_mean', 'color_rgb', 'color_hex',
    # Thread subclass exports
    'EmbThreadHus', 'EmbThreadJef', 'EmbThreadPec', 'EmbThreadSew', 'EmbThreadShv',
    # get_thread_set functions from all submodules
    'get_thread_set'
]
