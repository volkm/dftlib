from helpers.helper import get_example_path
import dftlib.io.parser
import dftlib.io.export
import dftlib.transformer.rewriting


def test_rewrite_small():
    file = get_example_path("simplify", "small.json")
    dft = dftlib.io.parser.parse_dft_json(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5

    dft = dftlib.transformer.rewriting.simplify_dft(dft)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
