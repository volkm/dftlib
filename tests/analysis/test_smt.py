import tempfile

from conftest import storm, z3
from helpers.helper import get_example_path

from dftlib.analysis.smt import SMTAnalysis


@storm
@z3
def test_smt_bounds():
    file = get_example_path("galileo", "mcs.dft")
    smt = SMTAnalysis()
    with tempfile.NamedTemporaryFile() as tmp_file:
        lower, upper, length = smt.check_eventually_fail(file, tmp_file.name)
        assert lower == 1
        assert upper == 8
        assert length == 12
