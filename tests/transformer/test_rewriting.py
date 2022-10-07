from helpers.helper import get_example_path

import dftlib.io.parser
import dftlib.transformer.simplifier as simplifier


def test_rewrite_all_small():
    file = get_example_path("simplify", "small.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3


def test_rewrite_all_gates():
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 19
    assert no_static == 5
    assert no_dynamic == 18
    assert no_elements == 42

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 19
    assert no_static == 6
    assert no_dynamic == 11
    assert no_elements == 36


def test_rewrite_all_be_types():
    file = get_example_path("json", "all_be_distributions.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 7
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 8

    changed = simplifier.simplify_dft_all_rules(dft)
    assert not changed
    # No simplification
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 7
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 8


def test_rewrite_parametric():
    file = get_example_path("json", "parametric.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3

    changed = simplifier.simplify_dft_all_rules(dft)
    assert not changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
