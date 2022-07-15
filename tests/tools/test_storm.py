from conftest import stormpy
from helpers.helper import get_example_path

import dftlib.io.export
import dftlib.io.parser


@stormpy
def test_load_galileo():
    file = get_example_path("galileo", "mcs.dft")
    dft = dftlib.io.parser.parse_dft_galileo(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 12
    assert no_static == 4
    assert no_dynamic == 5
    assert no_elements == 21
