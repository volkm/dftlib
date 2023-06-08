from conftest import stormpy
from helpers.helper import get_example_path

import dftlib.io.export_json
import dftlib.io.parser
import dftlib.storage.dft_be as dft_be


def test_load_json():
    file = get_example_path("json", "hecs.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 11
    assert no_static == 4
    assert no_dynamic == 7
    assert no_elements == 22


@stormpy
def test_load_galileo():
    file = get_example_path("galileo", "mcs.dft")
    dft = dftlib.io.parser.parse_dft_galileo_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 12
    assert no_static == 4
    assert no_dynamic == 5
    assert no_elements == 21


def test_load_parametric_json():
    file = get_example_path("json", "parametric.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 2
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 3
    assert dft.parametric()
    assert len(dft.parameters) == 2


@stormpy
def test_load_parametric_galileo():
    file = get_example_path("galileo", "parametric.dft")
    dft = dftlib.io.parser.parse_dft_galileo_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 1
    assert no_dynamic == 1
    assert no_elements == 5
    assert dft.parametric()
    assert len(dft.parameters) == 2


def test_load_txt():
    s = " AND(A, OR( B,C) ) "
    dft = dftlib.io.parser.parse_dft_txt_string(s)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5


def test_all_gates_types():
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 19
    assert no_static == 5
    assert no_dynamic == 18
    assert no_elements == 42


def test_all_be_types():
    file = get_example_path("json", "all_be_distributions.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 7
    assert no_static == 1
    assert no_dynamic == 0
    assert no_elements == 8
    assert isinstance(dft.get_element_by_name("A"), dft_be.BeConstant)
    assert isinstance(dft.get_element_by_name("B"), dft_be.BeConstant)
    assert isinstance(dft.get_element_by_name("C"), dft_be.BeProbability)
    assert isinstance(dft.get_element_by_name("D"), dft_be.BeExponential)
    assert isinstance(dft.get_element_by_name("E"), dft_be.BeErlang)
    assert isinstance(dft.get_element_by_name("F"), dft_be.BeLognormal)
    assert isinstance(dft.get_element_by_name("G"), dft_be.BeWeibull)
