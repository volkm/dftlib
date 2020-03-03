from helpers.helper import get_example_path

import dftlib.storage.dft as dfts


def test_create_dft():
    dft = dfts.Dft()

    be_a = dft.new_be("A", 5.0, 1, 0, (0, 0, 0, 0))
    be_b = dft.new_be("B", 3.0, 1, 0, (2, 2, 2, 2))
    and_t = dft.new_gate("T", "and", [be_a, be_b], (10, 10, 10, 10))
    dft.set_top_level_element(and_t.element_id)

    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    assert dft.top_level_element.element_id == 3
