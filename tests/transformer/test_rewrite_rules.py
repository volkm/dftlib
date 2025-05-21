from helpers.helper import get_example_path

import dftlib.io.parser
import dftlib.transformer.simplifier as simplifier
from dftlib.transformer.rewrite_rules import RewriteRules


def test_split_fdeps():
    file = get_example_path("simplify", "fdep.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 7

    while True:
        changed = simplifier.simplify_dft_rules(dft, [RewriteRules.SPLIT_FDEPS])
        if not changed:
            break
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 2
    assert no_dynamic == 3
    assert no_elements == 9


def test_rewrite_all_rule2():
    file = get_example_path("simplify", "rule2_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 3
    assert no_dynamic == 0
    assert no_elements == 5

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3

    file = get_example_path("simplify", "rule2_test2.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 5
    assert no_dynamic == 0
    assert no_elements == 7

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3


def test_rewrite_all_rule3():
    file = get_example_path("simplify", "rule3_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 3
    assert no_dynamic == 0
    assert no_elements == 4

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 2


def test_rewrite_all_rule5():
    file = get_example_path("simplify", "rule5_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 1
    assert no_dynamic == 2
    assert no_elements == 6

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 1
    assert no_dynamic == 1
    assert no_elements == 5
    pand = dft.top_level_element
    assert pand.element_type == "pand"
    children = pand.children()
    assert len(children) == 3
    assert children[0].name == "C"
    assert children[1].name == "D"
    assert children[2].name == "B2"


def test_rewrite_all_rule24():
    file = get_example_path("simplify", "rule24_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 6

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3

    file = get_example_path("simplify", "fdep.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 7

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 2


def test_rewrite_all_rule26():
    file = get_example_path("simplify", "rule26_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 6

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5


def test_rewrite_all_rule28():
    file = get_example_path("simplify", "rule28_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 2
    assert no_dynamic == 2
    assert no_elements == 6

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 1
    assert no_elements == 4


def test_rewrite_all_rule35():
    file = get_example_path("simplify", "rule35_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 6
    assert no_static == 5
    assert no_dynamic == 1
    assert no_elements == 12

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 5
    assert no_static == 3
    assert no_dynamic == 1
    assert no_elements == 9


def test_rewrite_all_fdep_cycle():
    file = get_example_path("simplify", "fdep_cycle.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 3
    assert no_dynamic == 2
    assert no_elements == 9

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 3
    assert no_dynamic == 1
    assert no_elements == 8


def test_merge_bes_parametric():
    file = get_example_path("json", "parametric.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    be_a = dft.get_element_by_name("A")
    assert be_a.dorm == 1
    assert be_a.rate == "(a)/(1)"
    be_b = dft.get_element_by_name("B")
    assert be_b.dorm == 1
    assert be_b.rate == "(b)/(1)"

    changed = simplifier.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 2
    be = dft.get_element_by_name("A_B")
    assert be.dorm == 1
    assert be.rate == "((a)/(1)) + ((b)/(1))"
