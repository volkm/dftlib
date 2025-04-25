import tempfile

from dftlib.exceptions.exceptions import ToolNotFound
from dftlib.utility.os_functions import run_tool

storm_path = ""

if storm_path:
    _has_storm = True
else:
    _has_storm = False


def requires_storm(func):
    """
    Decorator to check whether storm is available
    """

    def wrapper(*args, **kwargs):
        if _has_storm:
            return func(*args, **kwargs)
        else:
            raise ToolNotFound("Storm is required for this functionality.")

    return wrapper


@requires_storm
class Storm:
    """
    Class wrapping the storm model checker CLI.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.binary = storm_path

    def export_smt(self, file):
        # TODO replace by stormpy binding
        with tempfile.NamedTemporaryFile() as tmp_file:
            args = [self.binary, "-dft", file, "--export-smt", tmp_file.name]
            run_tool(args, True)
            with open(tmp_file.name, "r") as f:
                smt_encoding = f.read()
        return smt_encoding
