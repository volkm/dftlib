import dftlib.storage.dft as dfts
import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates


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
