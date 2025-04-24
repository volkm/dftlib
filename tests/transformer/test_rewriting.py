from helpers.helper import get_example_path
from conftest import stormpy

import dftlib.io.parser
import dftlib.storage.dft_gates as dft_gates
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
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 2


def test_rewrite_keep_order():
    file = get_example_path("simplify", "order.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 1
    assert no_elements == 4
    children = dft.top_level_element.children()
    assert children[0].name == "X"
    assert children[0].children()[0].name == "A"
    assert children[1].name == "B"

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 0
    assert no_dynamic == 1
    assert no_elements == 3
    children = dft.top_level_element.children()
    assert children[0].name == "A"
    assert children[1].name == "B"


@stormpy
def test_rewrite_replace_parents():
    file = get_example_path("simplify", "replace_parents.dft")
    dft = dftlib.io.parser.parse_dft_galileo_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 8
    assert no_static == 5
    assert no_dynamic == 3
    assert no_elements == 16
    children = dft.top_level_element.children()
    for child in children:
        assert isinstance(child, dft_gates.DftSpare)
        assert len(child.children()) == 2

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 1
    assert no_dynamic == 3
    assert no_elements == 8
    children = dft.top_level_element.children()
    for child in children:
        assert isinstance(child, dft_gates.DftSpare)
        assert len(child.children()) == 2
