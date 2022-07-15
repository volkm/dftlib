import tempfile

from dftlib.utility.os_functions import run_tool


class Storm:
    """
    Class wrapping the storm model checker CLI.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.binary = ""

    def export_smt(self, file):
        # TODO replace by stormpy binding
        with tempfile.NamedTemporaryFile() as tmp_file:
            args = [self.binary, '-dft', file, '--export-smt', tmp_file.name]
            run_tool(args, True)
            with open(tmp_file.name, "r") as f:
                smt_encoding = f.read()
        return smt_encoding
