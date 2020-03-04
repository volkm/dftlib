from helpers.helper import get_example_path

import dftlib.io.parser
import dftlib.io.export


def test_load_json():
    file = get_example_path("simplify", "HECS_re.json")
    dft = dftlib.io.parser.parse_dft_json(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 11
    assert no_static == 4
    assert no_dynamic == 7
    assert no_elements == 22


def test_all_types():
    file = get_example_path("json", "all_types.json")
    dft = dftlib.io.parser.parse_dft_json(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 7
    assert no_static == 3
    assert no_dynamic == 6
    assert no_elements == 16
