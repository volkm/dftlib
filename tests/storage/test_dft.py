from conftest import stormpy
from helpers.helper import get_example_path

import dftlib.io.parser
import dftlib.storage.dft as dfts
import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates
import dftlib.tools.stormpy as sp


def test_create_dft():
    dft = dfts.Dft()

    be_a = dft_be.BeExponential(dft.next_id(), "A", 5.0, 1, 0, (0, 0, 0, 0))
    dft.add(be_a)
    be_b = dft_be.BeExponential(dft.next_id(), "B", 3.0, 1, 0, (2, 2, 2, 2))
    dft.add(be_b)
    and_t = dft_gates.DftAnd(dft.next_id(), "T", [be_a, be_b], (10, 10, 10, 10))
    dft.add(and_t)
    dft.set_top_level_element(and_t.element_id)

    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    assert dft.top_level_element.element_id == 2
    assert dft.is_valid()


@stormpy
def test_convert_stormpy_dft():
    file = get_example_path("galileo", "mcs.dft")
    dft = dftlib.io.parser.parse_dft_galileo_file(file)
    assert dft.is_valid()
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 12
    assert no_static == 4
    assert no_dynamic == 5
    assert no_elements == 21

    sp_dft = sp.get_stormpy_dft(dft)
    assert sp_dft.nr_be() == 12
    assert sp_dft.nr_dynamic() == 5
    assert sp_dft.nr_elements() == 21
