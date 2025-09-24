"""Top-level module for PyStitch embroidery library"""

from typing import Optional, Union, Dict, Any, IO, Generator

# First-party imports (pystitch modules)
from pystitch.readers import A10oReader
from pystitch.readers import A100Reader

# pystitch.readers.ArtReader as ArtReader
from pystitch.readers import BroReader
from pystitch.readers import ColReader
from pystitch.readers import CsvReader
from pystitch.readers import DatReader
from pystitch.readers import DsbReader
from pystitch.readers import DstReader
from pystitch.readers import DszReader
from pystitch.readers import EdrReader
from pystitch.readers import EmdReader
from pystitch.readers import ExpReader
from pystitch.readers import ExyReader
from pystitch.readers import FxyReader
from pystitch.readers import GcodeReader
from pystitch.readers import GtReader
from pystitch.readers import HusReader
from pystitch.readers import InbReader
from pystitch.readers import InfReader
from pystitch.readers import IqpReader
from pystitch.readers import JefReader
from pystitch.readers import JpxReader
from pystitch.readers import JsonReader
from pystitch.readers import KsmReader
from pystitch.readers import MaxReader
from pystitch.readers import MitReader
from pystitch.readers import NewReader
from pystitch.readers import PcdReader
from pystitch.readers import PcmReader
from pystitch.readers import PcqReader
from pystitch.readers import PcsReader
from pystitch.readers import PecReader
from pystitch.readers import PesReader
from pystitch.readers import PhbReader
from pystitch.readers import PhcReader
from pystitch.readers import PltReader
from pystitch.readers import PmvReader
from pystitch.readers import QccReader
from pystitch.readers import SewReader
from pystitch.readers import ShvReader
from pystitch.readers import SpxReader
from pystitch.readers import StcReader
from pystitch.readers import StxReader
from pystitch.readers import TapReader
from pystitch.readers import TbfReader
from pystitch.readers import U01Reader
from pystitch.readers import Vp3Reader
from pystitch.readers import XxxReader
from pystitch.readers import ZhsReader
from pystitch.readers import ZxyReader

# Writers
from pystitch.writers import ColWriter
from pystitch.writers import CsvWriter
from pystitch.writers import DstWriter
from pystitch.writers import EdrWriter
from pystitch.writers import ExpWriter
from pystitch.writers import GcodeWriter
from pystitch.writers import InkstitchGcodeWriter
from pystitch.writers import InfWriter
from pystitch.writers import JefWriter
from pystitch.writers import JsonWriter
from pystitch.writers import PecWriter
from pystitch.writers import PesWriter
from pystitch.writers import PltWriter
from pystitch.writers import PmvWriter
from pystitch.writers import PngWriter
from pystitch.writers import QccWriter
from pystitch.writers import SvgWriter
from pystitch.writers import TbfWriter
from pystitch.writers import TxtWriter
from pystitch.writers import U01Writer
from pystitch.writers import Vp3Writer
from pystitch.writers import XxxWriter

# Local imports from organized modules
from .core.EmbConstant import *
from .core.EmbPattern import EmbPattern
from .core.pystitch import *
from .utils.EmbFunctions import *
from .utils.EmbCompress import compress, expand  # type: ignore # noqa: F401

# items available in a sub-heirarchy (e.g. pystitch.PecGraphics.get_graphic_as_string)
from .utils.PecGraphics import get_graphic_as_string  # type: ignore


def read(filename: str, settings: Optional[Dict[str, Any]] = None,
         pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads file, assuming type by extension"""
    extension = EmbPattern.get_extension_by_filename(filename)  # type: ignore
    extension = extension.lower()  # type: ignore
    for file_type in supported_formats():
        if file_type["extension"] != extension:
            continue
        reader = file_type.get("reader", None)  # type: ignore
        return EmbPattern.read_embroidery(reader, filename, settings, pattern)  # type: ignore
    return None


def write(pattern: 'EmbPattern', filename: str, settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes file, assuming type by extension"""
    extension = EmbPattern.get_extension_by_filename(filename)  # type: ignore
    extension = extension.lower()  # type: ignore
    supported_extensions = [file_type["extension"]
                           for file_type in supported_formats()]  # type: ignore

    if extension not in supported_extensions:  # type: ignore
        raise IOError(f"Conversion to file type '{extension}' is not supported")  # type: ignore

    ext_to_file_type_lookup = {file_type["extension"]: file_type
                              for file_type in supported_formats()}  # type: ignore
    writer = ext_to_file_type_lookup[extension].get("writer")  # type: ignore

    if writer:
        EmbPattern.write_embroidery(writer, pattern, filename, settings)  # type: ignore
    else:
        raise IOError("No supported writer found.")

def convert(filename_from: str, filename_to: str,
           settings: Optional[Dict[str, Any]] = None) -> None:
    """Convert embroidery file from one format to another"""
    pattern = read(filename_from, settings)
    if pattern is None:
        return
    write(pattern, filename_to, settings)

def supported_formats() -> Generator[Dict[str, Any], None, None]:
    """Generates dictionary entries for supported formats. Each entry will
    always have description, extension, mimetype, and category. Reader
    will provide the reader, if one exists, writer will provide the writer,
    if one exists.

    Metadata gives a list of metadata read and/or written by that type.

    Options provides accepted options by the format and their accepted values.
    """
    # yield ({
    #     "description": "Art Embroidery Format",
    #     "extension": "art",
    #     "extensions": ("art",),
    #     "mimetype": "application/x-art",
    #     "category": "embroidery",
    #     "reader": ArtReader,
    #     "metadata": ("name")
    # })
    yield (
        {
            "description": "Brother Embroidery Format",
            "extension": "pec",
            "extensions": ("pec",),
            "mimetype": "application/x-pec",
            "category": "embroidery",
            "reader": PecReader,
            "writer": PecWriter,
            "metadata": ("name"),
        }
    )
    yield (
        {
            "description": "Brother Embroidery Format",
            "extension": "pes",
            "extensions": ("pes",),
            "mimetype": "application/x-pes",
            "category": "embroidery",
            "reader": PesReader,
            "writer": PesWriter,
            "versions": ("1", "6", "1t", "6t"),
            "metadata": ("name", "author", "category", "keywords", "comments"),
        }
    )
    yield (
        {
            "description": "Melco Expanded Embroidery Format",
            "extension": "exp",
            "extensions": ("exp",),
            "mimetype": "application/x-exp",
            "category": "embroidery",
            "reader": ExpReader,
            "writer": ExpWriter,
        }
    )
    # yield (
    #     {
    #         "description": "Melco Condensed Embroidery Format",
    #         "extension": "cnd",
    #         "extensions": ("cnd",),
    #         "mimetype": "application/x-cnd",
    #         "category": "embroidery",
    #         "reader": CndReader,
    #     }
    # )
    yield (
        {
            "description": "Tajima Embroidery Format",
            "extension": "dst",
            "extensions": ("dst",),
            "mimetype": "application/x-dst",
            "category": "embroidery",
            "reader": DstReader,
            "writer": DstWriter,
            "read_options": {
                "trim_distance": (None, 3.0, 50.0),
                "trim_at": (2, 3, 4, 5, 6, 7, 8),
                "clipping": (True, False),
            },
            "write_options": {"trim_at": (2, 3, 4, 5, 6, 7, 8)},
            "versions": ("default", "extended"),
            "metadata": ("name", "author", "copyright"),
        }
    )
    yield (
        {
            "description": "Janome Embroidery Format",
            "extension": "jef",
            "extensions": ("jef",),
            "mimetype": "application/x-jef",
            "category": "embroidery",
            "reader": JefReader,
            "writer": JefWriter,
            "read_options": {
                "trim_distance": (None, 3.0, 50.0),
                "trims": (True, False),
                "trim_at": (2, 3, 4, 5, 6, 7, 8),
                "clipping": (True, False),
            },
            "write_options": {
                "trims": (True, False),
                "trim_at": (2, 3, 4, 5, 6, 7, 8),
            },
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "vp3",
            "extensions": ("vp3",),
            "mimetype": "application/x-vp3",
            "category": "embroidery",
            "reader": Vp3Reader,
            "writer": Vp3Writer,
        }
    )
    yield (
        {
            "description": "Scalable Vector Graphics",
            "extension": "svg",
            "extensions": ("svg", "svgz"),
            "mimetype": "image/svg+xml",
            "category": "vector",
            "writer": SvgWriter,
        }
    )
    yield (
        {
            "description": "Comma-separated values",
            "extension": "csv",
            "extensions": ("csv",),
            "mimetype": "text/csv",
            "category": "debug",
            "reader": CsvReader,
            "writer": CsvWriter,
            "versions": ("default", "delta", "full"),
        }
    )
    yield (
        {
            "description": "Singer Embroidery Format",
            "extension": "xxx",
            "extensions": ("xxx",),
            "mimetype": "application/x-xxx",
            "category": "embroidery",
            "reader": XxxReader,
            "writer": XxxWriter,
        }
    )
    yield (
        {
            "description": "Janome Embroidery Format",
            "extension": "sew",
            "extensions": ("sew",),
            "mimetype": "application/x-sew",
            "category": "embroidery",
            "reader": SewReader,
        }
    )
    yield (
        {
            "description": "Barudan Embroidery Format",
            "extension": "u01",
            "extensions": ("u00", "u01", "u02"),
            "mimetype": "application/x-u01",
            "category": "embroidery",
            "reader": U01Reader,
            "writer": U01Writer,
        }
    )
    yield (
        {
            "description": "Husqvarna Viking Embroidery Format",
            "extension": "shv",
            "extensions": ("shv",),
            "mimetype": "application/x-shv",
            "category": "embroidery",
            "reader": ShvReader,
        }
    )
    yield (
        {
            "description": "Toyota Embroidery Format",
            "extension": "10o",
            "extensions": ("10o",),
            "mimetype": "application/x-10o",
            "category": "embroidery",
            "reader": A10oReader,
        }
    )
    yield (
        {
            "description": "Toyota Embroidery Format",
            "extension": "100",
            "extensions": ("100",),
            "mimetype": "application/x-100",
            "category": "embroidery",
            "reader": A100Reader,
        }
    )
    yield (
        {
            "description": "Bits & Volts Embroidery Format",
            "extension": "bro",
            "extensions": ("bro",),
            "mimetype": "application/x-Bro",
            "category": "embroidery",
            "reader": BroReader,
        }
    )
    yield (
        {
            "description": "Sunstar or Barudan Embroidery Format",
            "extension": "dat",
            "extensions": ("dat",),
            "mimetype": "application/x-dat",
            "category": "embroidery",
            "reader": DatReader,
        }
    )
    yield (
        {
            "description": "Tajima(Barudan) Embroidery Format",
            "extension": "dsb",
            "extensions": ("dsb",),
            "mimetype": "application/x-dsb",
            "category": "embroidery",
            "reader": DsbReader,
        }
    )
    yield (
        {
            "description": "ZSK USA Embroidery Format",
            "extension": "dsz",
            "extensions": ("dsz",),
            "mimetype": "application/x-dsz",
            "category": "embroidery",
            "reader": DszReader,
        }
    )
    yield (
        {
            "description": "Elna Embroidery Format",
            "extension": "emd",
            "extensions": ("emd",),
            "mimetype": "application/x-emd",
            "category": "embroidery",
            "reader": EmdReader,
        }
    )
    yield (
        {
            "description": "Eltac Embroidery Format",
            "extension": "exy",  # e??, e01
            "extensions": ("e00", "e01", "e02"),
            "mimetype": "application/x-exy",
            "category": "embroidery",
            "reader": ExyReader,
        }
    )
    yield (
        {
            "description": "Fortron Embroidery Format",
            "extension": "fxy",  # f??, f01
            "extensions": ("f00", "f01", "f02"),
            "mimetype": "application/x-fxy",
            "category": "embroidery",
            "reader": FxyReader,
        }
    )
    yield (
        {
            "description": "Gold Thread Embroidery Format",
            "extension": "gt",
            "extensions": ("gt",),
            "mimetype": "application/x-exy",
            "category": "embroidery",
            "reader": GtReader,
        }
    )
    yield (
        {
            "description": "Inbro Embroidery Format",
            "extension": "inb",
            "extensions": ("inb",),
            "mimetype": "application/x-inb",
            "category": "embroidery",
            "reader": InbReader,
        }
    )
    yield (
        {
            "description": "Tajima Embroidery Format",
            "extension": "tbf",
            "extensions": ("tbf",),
            "mimetype": "application/x-tbf",
            "category": "embroidery",
            "reader": TbfReader,
            "writer": TbfWriter,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "ksm",
            "extensions": ("ksm",),
            "mimetype": "application/x-ksm",
            "category": "embroidery",
            "reader": KsmReader,
        }
    )
    yield (
        {
            "description": "Happy Embroidery Format",
            "extension": "tap",
            "extensions": ("tap",),
            "mimetype": "application/x-tap",
            "category": "embroidery",
            "reader": TapReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "spx",
            "extensions": ("spx"),
            "mimetype": "application/x-spx",
            "category": "embroidery",
            "reader": SpxReader,
        }
    )
    yield (
        {
            "description": "Data Stitch Embroidery Format",
            "extension": "stx",
            "extensions": ("stx",),
            "mimetype": "application/x-stx",
            "category": "embroidery",
            "reader": StxReader,
        }
    )
    yield (
        {
            "description": "Brother Embroidery Format",
            "extension": "phb",
            "extensions": ("phb",),
            "mimetype": "application/x-phb",
            "category": "embroidery",
            "reader": PhbReader,
        }
    )
    yield (
        {
            "description": "Brother Embroidery Format",
            "extension": "phc",
            "extensions": ("phc",),
            "mimetype": "application/x-phc",
            "category": "embroidery",
            "reader": PhcReader,
        }
    )
    yield (
        {
            "description": "Ameco Embroidery Format",
            "extension": "new",
            "extensions": ("new",),
            "mimetype": "application/x-new",
            "category": "embroidery",
            "reader": NewReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "max",
            "extensions": ("max",),
            "mimetype": "application/x-max",
            "category": "embroidery",
            "reader": MaxReader,
        }
    )
    yield (
        {
            "description": "Mitsubishi Embroidery Format",
            "extension": "mit",
            "extensions": ("mit",),
            "mimetype": "application/x-mit",
            "category": "embroidery",
            "reader": MitReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "pcd",
            "extensions": ("pcd",),
            "mimetype": "application/x-pcd",
            "category": "embroidery",
            "reader": PcdReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "pcq",
            "extensions": ("pcq",),
            "mimetype": "application/x-pcq",
            "category": "embroidery",
            "reader": PcqReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "pcm",
            "extensions": ("pcm",),
            "mimetype": "application/x-pcm",
            "category": "embroidery",
            "reader": PcmReader,
        }
    )
    yield (
        {
            "description": "Pfaff Embroidery Format",
            "extension": "pcs",
            "extensions": ("pcs",),
            "mimetype": "application/x-pcs",
            "category": "embroidery",
            "reader": PcsReader,
        }
    )
    yield (
        {
            "description": "Janome Embroidery Format",
            "extension": "jpx",
            "extensions": ("jpx",),
            "mimetype": "application/x-jpx",
            "category": "embroidery",
            "reader": JpxReader,
        }
    )
    yield (
        {
            "description": "Gunold Embroidery Format",
            "extension": "stc",
            "extensions": ("stc",),
            "mimetype": "application/x-stc",
            "category": "embroidery",
            "reader": StcReader,
        }
    )
    yield ({
        "description": "Zeng Hsing Embroidery Format",
        "extension": "zhs",
        "extensions": ("zhs",),
        "mimetype": "application/x-zhs",
        "category": "embroidery",
        "reader": ZhsReader
    })
    yield (
        {
            "description": "ZSK TC Embroidery Format",
            "extension": "zxy",
            "extensions": ("z00", "z01", "z02"),
            "mimetype": "application/x-zxy",
            "category": "embroidery",
            "reader": ZxyReader,
        }
    )
    yield (
        {
            "description": "Brother Stitch Format",
            "extension": "pmv",
            "extensions": ("pmv",),
            "mimetype": "application/x-pmv",
            "category": "stitch",
            "reader": PmvReader,
            "writer": PmvWriter,
        }
    )
    yield (
        {
            "description": "PNG Format, Portable Network Graphics",
            "extension": "png",
            "extensions": ("png",),
            "mimetype": "image/png",
            "category": "image",
            "writer": PngWriter,
            "write_options": {
                "background": (0x000000, 0xFFFFFF),
                "linewidth": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
            },
        }
    )
    yield (
        {
            "description": "txt Format, Text File",
            "extension": "txt",
            "extensions": ("txt",),
            "mimetype": "text/plain",
            "category": "debug",
            "writer": TxtWriter,
            "versions": ("default", "embroidermodder"),
        }
    )
    yield (
        {
            "description": "gcode Format, Text File",
            "extension": "gcode",
            "extensions": ("gcode", "g-code", "ngc", "nc", ".g"),
            "mimetype": "text/plain",
            "category": "embroidery",
            "reader": GcodeReader,
            "writer": InkstitchGcodeWriter,
            "write_options": {
                "flip_x": (True, False),
                "flip_y": (True, False),
                "alternate_z": (True, False),
                "stitch_z_travel": (int),
            },
        }
    )
    yield (
        {
            "description": "Husqvarna Embroidery Format",
            "extension": "hus",
            "extensions": ("hus",),
            "mimetype": "application/x-hus",
            "category": "embroidery",
            "reader": HusReader,
        }
    )
    yield(
        {
            "description": "Iqp - Intelliquilter Format",
            "extension": "iqp",
            "extensions": ("iqp",),
            "mimetype": "application/x-iqp",
            "category": "quilting",
            "reader": IqpReader,
        }
    )
    yield(
        {
            "description": "Plt - HPGL",
            "extension": "plt",
            "extensions": ("plt",),
            "mimetype": "text/plain",
            "category": "quilting",
            "reader": PltReader,
            "writer": PltWriter,
        }
    )
    yield(
        {
            "description": "Qcc - QuiltEZ",
            "extension": "qcc",
            "extensions": ("qcc",),
            "mimetype": "text/plain",
            "category": "quilting",
            "reader": QccReader,
            "writer": QccWriter,
        }
    )
    yield (
        {
            "description": "Edr Color Format",
            "extension": "edr",
            "extensions": ("edr",),
            "mimetype": "application/x-edr",
            "category": "color",
            "reader": EdrReader,
            "writer": EdrWriter,
        }
    )
    yield (
        {
            "description": "Col Color Format",
            "extension": "col",
            "extensions": ("col",),
            "mimetype": "application/x-col",
            "category": "color",
            "reader": ColReader,
            "writer": ColWriter,
        }
    )
    yield (
        {
            "description": "Inf Color Format",
            "extension": "inf",
            "extensions": ("inf",),
            "mimetype": "application/x-inf",
            "category": "color",
            "reader": InfReader,
            "writer": InfWriter,
        }
    )
    yield (
        {
            "description": "Json Export",
            "extension": "json",
            "extensions": ("json",),
            "mimetype": "application/json",
            "category": "debug",
            "reader": JsonReader,
            "writer": JsonWriter,
        }
    )

def read_dst(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as DST file"""
    return EmbPattern.read_embroidery(DstReader, f, settings, pattern)  # type: ignore

def read_pec(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as PEC file"""
    return EmbPattern.read_embroidery(PecReader, f, settings, pattern)  # type: ignore

def read_pes(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as PES file"""
    return EmbPattern.read_embroidery(PesReader, f, settings, pattern)  # type: ignore

def read_exp(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as EXP file"""
    return EmbPattern.read_embroidery(ExpReader, f, settings, pattern)  # type: ignore

def read_vp3(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as VP3 file"""
    return EmbPattern.read_embroidery(Vp3Reader, f, settings, pattern)  # type: ignore

def read_jef(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as JEF file"""
    return EmbPattern.read_embroidery(JefReader, f, settings, pattern)  # type: ignore

def read_u01(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as U01 file"""
    return EmbPattern.read_embroidery(U01Reader, f, settings, pattern)  # type: ignore

def read_csv(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as CSV file"""
    return EmbPattern.read_embroidery(CsvReader, f, settings, pattern)  # type: ignore

def read_json(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
             pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as JSON file"""
    return EmbPattern.read_embroidery(JsonReader, f, settings, pattern)  # type: ignore

def read_gcode(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
              pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as GCode file"""
    return EmbPattern.read_embroidery(GcodeReader, f, settings, pattern)  # type: ignore

def read_xxx(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as XXX file"""
    return EmbPattern.read_embroidery(XxxReader, f, settings, pattern)  # type: ignore

def read_tbf(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as TBF file"""
    return EmbPattern.read_embroidery(TbfReader, f, settings, pattern)  # type: ignore

def read_iqp(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as IQP file"""
    pattern = EmbPattern.read_embroidery(IqpReader, f, settings, pattern)  # type: ignore
    return pattern  # type: ignore

def read_plt(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as PLT file"""
    pattern = EmbPattern.read_embroidery(PltReader, f, settings, pattern)  # type: ignore
    return pattern  # type: ignore

def read_qcc(f: Union[str, IO[Any]], settings: Optional[Dict[str, Any]] = None,
            pattern: Optional['EmbPattern'] = None) -> Optional['EmbPattern']:
    """Reads fileobject as QCC file"""
    pattern = EmbPattern.read_embroidery(QccReader, f, settings, pattern)  # type: ignore
    return pattern  # type: ignore

def write_dst(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as DST file"""
    EmbPattern.write_embroidery(DstWriter, pattern, stream, settings)  # type: ignore

def write_pec(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as PEC file"""
    EmbPattern.write_embroidery(PecWriter, pattern, stream, settings)  # type: ignore

def write_pes(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as PES file"""
    EmbPattern.write_embroidery(PesWriter, pattern, stream, settings)  # type: ignore

def write_exp(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as EXP file"""
    EmbPattern.write_embroidery(ExpWriter, pattern, stream, settings)  # type: ignore

def write_vp3(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as Vp3 file"""
    EmbPattern.write_embroidery(Vp3Writer, pattern, stream, settings)  # type: ignore

def write_jef(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as JEF file"""
    EmbPattern.write_embroidery(JefWriter, pattern, stream, settings)  # type: ignore

def write_u01(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as U01 file"""
    EmbPattern.write_embroidery(U01Writer, pattern, stream, settings)  # type: ignore

def write_csv(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as CSV file"""
    EmbPattern.write_embroidery(CsvWriter, pattern, stream, settings)  # type: ignore

def write_json(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
              settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as JSON file"""
    EmbPattern.write_embroidery(JsonWriter, pattern, stream, settings)  # type: ignore

def write_txt(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as TXT file"""
    EmbPattern.write_embroidery(TxtWriter, pattern, stream, settings)  # type: ignore

def write_gcode(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
               settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as Gcode file"""
    EmbPattern.write_embroidery(GcodeWriter, pattern, stream, settings)  # type: ignore

def write_xxx(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as XXX file"""
    EmbPattern.write_embroidery(XxxWriter, pattern, stream, settings)  # type: ignore

def write_tbf(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as TBF file"""
    EmbPattern.write_embroidery(TbfWriter, pattern, stream, settings)  # type: ignore

def write_plt(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as PLT file"""
    EmbPattern.write_embroidery(PltWriter, pattern, stream, settings)  # type: ignore

def write_qcc(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as QCC file"""
    EmbPattern.write_embroidery(QccWriter, pattern, stream, settings)  # type: ignore

def write_svg(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as SVG file"""
    EmbPattern.write_embroidery(SvgWriter, pattern, stream, settings)  # type: ignore

def write_png(pattern: 'EmbPattern', stream: Union[str, IO[Any]],
             settings: Optional[Dict[str, Any]] = None) -> None:
    """Writes fileobject as PNG file"""
    EmbPattern.write_embroidery(PngWriter, pattern, stream, settings)  # type: ignore
