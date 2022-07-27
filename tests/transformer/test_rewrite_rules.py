from helpers.helper import get_example_path

import dftlib.io.parser
import dftlib.transformer.rewrite_rules as rewrite_rules
import dftlib.transformer.rewriting


def test_split_fdeps():
    file = get_example_path("simplify", "fdep.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 7

    changed = rewrite_rules.split_fdeps(dft)
    assert changed
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

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 4
    # TODO should yield single AND with both BEs using all rewrite rules

    file = get_example_path("simplify", "rule2_test2.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 5
    assert no_dynamic == 0
    assert no_elements == 7

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 3
    assert no_dynamic == 0
    assert no_elements == 5
    # TODO should yield single OR with both BEs using all rewrite rules


def test_rewrite_all_rule3():
    file = get_example_path("simplify", "rule3_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 3
    assert no_dynamic == 0
    assert no_elements == 4

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 1
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 2
    # TODO should yield single BE using all rewrite rules


def test_rewrite_all_rule24():
    file = get_example_path("simplify", "rule24_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 6

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 3
    assert no_dynamic == 0
    assert no_elements == 6
    # TODO should yield single BE using all rewrite rules

    file = get_example_path("simplify", "fdep.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 7

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 4
    assert no_static == 5
    assert no_dynamic == 0
    assert no_elements == 9
    # TODO should yield single BE "C" using all rewrite rules


def test_rewrite_all_rule26():
    file = get_example_path("simplify", "rule26_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 1
    assert no_elements == 6

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5
    # TODO could be further simplified if TLE is not relevant


def test_rewrite_all_rule28():
    file = get_example_path("simplify", "rule28_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 2
    assert no_dynamic == 2
    assert no_elements == 6

    changed = dftlib.transformer.rewriting.simplify_dft_all_rules(dft)
    assert changed
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 1
    assert no_elements == 4
    # TODO could be further simplified if TLE is not relevant
