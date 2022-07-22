import dftlib.storage.dft as dfts
import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates
from dftlib.transformer.trimming import trim


def test_trim():
    dft = dfts.Dft()
    be_a = dft_be.BeExponential(0, "A", 5.0, 1, 0, (0, 0, 0, 0))
    dft.add(be_a)
    be_b = dft_be.BeExponential(1, "B", 3.0, 1, 0, (2, 2, 2, 2))
    dft.add(be_b)
    be_c = dft_be.BeExponential(2, "C", 1.0, 1, 0, (2, 2, 2, 2))
    dft.add(be_c)
    and_t = dft_gates.DftAnd(3, "T", [be_a, be_b], (10, 10, 10, 10))
    dft.add(and_t)
    dft.set_top_level_element(and_t.element_id)

    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 4
    assert dft.top_level_element.element_id == 3

    trim(dft)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    assert dft.top_level_element.element_id == 3
