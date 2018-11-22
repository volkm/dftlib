from helpers.helper import get_example_path
import dft_tool.io.parser
import dft_tool.io.export
import dft_tool.transformer.rewriting


def test_rewrite_small():
    file = get_example_path("simplify", "small.json")
    dft = dft_tool.io.parser.parse_dft_json(file)
    no_be, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_dynamic == 0
    assert no_elements == 5

    dft_tool.transformer.rewriting.simplify_dft(dft)
    no_be, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_dynamic == 0
    assert no_elements == 3
