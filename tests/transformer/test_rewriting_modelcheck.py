from helpers.helper import get_example_path
from conftest import stormpy

import math


import dftlib.io.parser
from dftlib.storage.dft import Dft
import dftlib.transformer.simplifier as simplifier
import dftlib.tools.stormpy as sp


def simplify_and_check(dft: Dft, formulas: list[str]):
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    # Check that initial DFT is valid
    dft.check_valid()
    # Model check
    results_baseline = [sp.analyze_dft(dft, formula) for formula in formulas]

    rules = simplifier.get_all_rules()
    steps = 0
    while True:
        rule, element = simplifier.apply_rules(dft, rules)
        if rule is None:
            # No rule could be applied
            break
        else:
            # Dft was changed
            steps += 1
            # Check that dft stays valid
            dft.check_valid()
            # Model check
            results = [sp.analyze_dft(dft, formula) for formula in formulas]
            # Compare to baseline
            assert all((math.isclose(r1, r2) for r1, r2 in zip(results, results_baseline)))

    assert steps > 0
    no_be_simple, no_static_simple, no_dynamic_simple, no_elements_simple = dft.statistics()
    assert no_be >= no_be_simple
    assert no_elements >= no_elements_simple


# Omit galileo/mcs.dft because no simplification is possible
# Omit galileo/parametric.dft because it is parametric
# Omit json/all_be_distributions.json because not all distributions are supported for model checking
# Omit json/all_gates.json because exclusive PAND is not supported for analysis


@stormpy
def test_rewrite_hecs():
    file = get_example_path("json", "hecs.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['Tmin=? [ F "failed" ]', 'Pmin=? [ F<=1 "failed" ]'])


# Omit json/parametric.json because it is parametric
# Omit simplify/fdep.json because it contains non-binary FDEPs


@stormpy
def test_rewrite_fdep_cycle():
    file = get_example_path("simplify", "fdep_cycle.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_order():
    file = get_example_path("simplify", "order.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_parents():
    file = get_example_path("simplify", "replace_parents.dft")
    dft = dftlib.io.parser.parse_dft_galileo_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule2():
    file = get_example_path("simplify", "rule2_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])
    file = get_example_path("simplify", "rule2_test2.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule3():
    file = get_example_path("simplify", "rule3_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule5():
    file = get_example_path("simplify", "rule5_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule24():
    file = get_example_path("simplify", "rule24_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule26():
    file = get_example_path("simplify", "rule26_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule28():
    file = get_example_path("simplify", "rule28_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule35():
    file = get_example_path("simplify", "rule35_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_rule36():
    file = get_example_path("simplify", "rule36_test.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])


@stormpy
def test_rewrite_small():
    file = get_example_path("simplify", "small.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    simplify_and_check(dft, ['T=? [ F "failed" ]', 'P=? [ F<=1 "failed" ]'])
