from dftlib.io.export_json import export_dft_string
from dftlib.storage.dft import Dft
from dftlib.exceptions.exceptions import ToolNotFound

"""
File wrapping the stormpy bindings for the Storm model checker.
"""

try:
    import stormpy as _stormpy
    import stormpy.dft
except ImportError:
    _has_stormpy = False
else:
    _has_stormpy = True


def requires_stormpy(func):
    """
    Decorator to check whether stormpy is available
    """

    def wrapper(*args, **kwargs):
        if _has_stormpy:
            return func(*args, **kwargs)
        else:
            raise ToolNotFound("stormpy is required for this functionality.")

    return wrapper


@requires_stormpy
def convert_to_json(file: str) -> str:
    """
    Convert galileo file to json string.
    :param file: Galileo file.
    :return: JSON string of the DFT.
    """
    # Check whether the file contains a parametric DFT
    parametric = False
    with open(file) as f:
        # Check whether the file starts with 'param xyz;'
        if f.readline().startswith("param"):
            parametric = True
    if parametric:
        dft_stormpy = _stormpy.dft.load_parametric_dft_galileo_file(file)
        return _stormpy.dft.export_parametric_dft_json_string(dft_stormpy)
    else:
        dft_stormpy = _stormpy.dft.load_dft_galileo_file(file)
        return _stormpy.dft.export_dft_json_string(dft_stormpy)


@requires_stormpy
def get_stormpy_dft(dft: Dft) -> "stormpy.dft.DFT_double | stormpy.dft.DFT_ratfunc":
    """
    Convert DFT to representation in stormpy.
    :param dft: DFT as dftlib object.
    :return: DFT as stormpy object.
    """
    json_string = export_dft_string(dft, indent=None)
    if dft.parametric():
        return _stormpy.dft.load_parametric_dft_json_string(json_string)
    else:
        return _stormpy.dft.load_dft_json_string(json_string)


@requires_stormpy
def analyze_dft(dft: Dft, formula: str) -> float:
    # Parse formula in stormpy format
    formulas = _stormpy.parse_properties(formula)
    # Convert DFT to stormpy DFT
    sp_dft = get_stormpy_dft(dft)
    # Model check
    results = _stormpy.dft.analyze_dft(sp_dft, [formulas[0].raw_formula])
    return results[0]
