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
def convert_to_json(file):
    """
    Convert galileo file to json string.
    :param file: Galileo file.
    :return: JSON string of the DFT.
    """
    dft_stormpy = _stormpy.dft.load_dft_galileo_file(file)
    return _stormpy.dft.export_dft_json_string(dft_stormpy)