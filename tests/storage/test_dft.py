import dftlib.storage.dft as dfts
import dftlib.storage.dft_elements as dft_elements


def test_create_dft():
    dft = dfts.Dft()

    be_a = dft_elements.DftBe(0, "A", 5.0, 1, 0, (0, 0, 0, 0))
    dft.add(be_a)
    be_b = dft_elements.DftBe(1, "B", 3.0, 1, 0, (2, 2, 2, 2))
    dft.add(be_b)
    and_t = dft_elements.DftAnd(2, "T", [be_a, be_b], (10, 10, 10, 10))
    dft.add(and_t)
    dft.set_top_level_element(and_t.element_id)

    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    assert dft.top_level_element.element_id == 2
