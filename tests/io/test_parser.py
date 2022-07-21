from conftest import stormpy
from helpers.helper import get_example_path

import dftlib.io.export
import dftlib.io.parser


def test_load_json():
    file = get_example_path("simplify", "HECS_re.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 11
    assert no_static == 4
    assert no_dynamic == 7
    assert no_elements == 22


@stormpy
def test_load_galileo():
    file = get_example_path("galileo", "mcs.dft")
    dft = dftlib.io.parser.parse_dft_galileo(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 12
    assert no_static == 4
    assert no_dynamic == 5
    assert no_elements == 21


def test_all_gates_types():
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 19
    assert no_static == 5
    assert no_dynamic == 18
    assert no_elements == 42
