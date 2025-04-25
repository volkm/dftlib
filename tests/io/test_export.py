import os

from conftest import stormpy
from helpers.helper import get_example_path

import dftlib.io.export_galileo
import dftlib.io.export_json
import dftlib.io.export_txt
import dftlib.io.parser


def test_export_galileo(tmpdir):
    file = get_example_path("json", "hecs.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "hecs.dft")
    dftlib.io.export_galileo.export_dft_file(dft, tmp_path)

    expected_lines = [
        'toplevel "HECS";',
        '"HECS" or "MSF" "PSF" "HW_SW_BUS1_BUS2";',
        '"MSF" vot3 "M1" "M2" "M3" "M4" "M5";',
        '"PSF" and "P1" "P2";',
        '"HW_SW_BUS1_BUS2" lambda=0.030052000000000002 dorm=0.0;',
        '"M1" lambda=6e-05 dorm=0.0;',
        '"M2" lambda=6e-05 dorm=0.0;',
        '"M3" lambda=6e-05 dorm=0.0;',
        '"M4" lambda=6e-05 dorm=0.0;',
        '"M5" lambda=6e-05 dorm=0.0;',
        '"P1" wsp "A1" "AS";',
        '"P2" wsp "A2" "AS";',
        '"A1" lambda=0.0001 dorm=0.0;',
        '"AS" lambda=0.0001 dorm=0.0;',
        '"A2" lambda=0.0001 dorm=0.0;',
        '"MIU" and "MIU1" "MIU2";',
        '"MIU1" lambda=5e-05 dorm=0.0;',
        '"MIU2" lambda=5e-05 dorm=0.0;',
        '"FDEP_A" fdep "MIU" "M3";',
        '"FDEP_B" fdep "MIU1" "M1";',
        '"FDEP_C" fdep "MIU2" "M5";',
        '"FDEP_25" fdep "MIU1" "M2";',
        '"FDEP_26" fdep "MIU2" "M4";',
    ]

    tmp_file = open(tmp_path, "r").read().splitlines()
    for i in range(0, len(tmp_file)):
        assert tmp_file[i] == expected_lines[i]


def test_export_json_all_gates(tmpdir):
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "all_gates.json")
    dftlib.io.export_json.export_dft_file(dft, tmp_path)
    dft2 = dftlib.io.parser.parse_dft_json_file(tmp_path)

    assert dft.compare(dft2, respect_ids=True)


def test_export_json_all_be(tmpdir):
    file = get_example_path("json", "all_be_distributions.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "all_be_distributions.json")
    dftlib.io.export_json.export_dft_file(dft, tmp_path)
    dft2 = dftlib.io.parser.parse_dft_json_file(tmp_path)

    assert dft.compare(dft2, respect_ids=True)


def test_export_json_string_all_gates():
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    json_string = dftlib.io.export_json.export_dft_string(dft)
    dft2 = dftlib.io.parser.parse_dft_json_string(json_string)

    assert dft.compare(dft2, respect_ids=True)


def test_export_json_string_all_be():
    file = get_example_path("json", "all_be_distributions.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    json_string = dftlib.io.export_json.export_dft_string(dft)
    dft2 = dftlib.io.parser.parse_dft_json_string(json_string)

    assert dft.compare(dft2, respect_ids=True)


@stormpy
def test_export_galileo_all_gates(tmpdir):
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "all_gates.dft")
    dftlib.io.export_galileo.export_dft_file(dft, tmp_path)
    dft2 = dftlib.io.parser.parse_dft_galileo_file(tmp_path)

    assert dft.compare(dft2, respect_ids=False)


@stormpy
def test_export_galileo_all_be(tmpdir):
    file = get_example_path("json", "all_be_distributions.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "all_be_distributions.dft")
    dftlib.io.export_galileo.export_dft_file(dft, tmp_path)
    dft2 = dftlib.io.parser.parse_dft_galileo_file(tmp_path)

    assert dft.compare(dft2, respect_ids=True)


def test_export_json_parametric(tmpdir):
    file = get_example_path("json", "parametric.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "parametric.json")
    dftlib.io.export_json.export_dft_file(dft, tmp_path)
    dft2 = dftlib.io.parser.parse_dft_json_file(tmp_path)

    assert dft.compare(dft2, respect_ids=True)
    assert set(dft.parameters) == set(dft2.parameters)


def test_export_txt_string():
    file = get_example_path("simplify", "rule2_test2.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    txt_string = dftlib.io.export_txt.export_dft_string(dft)
    assert txt_string == "AND(AND(BE0,BE1),AND(BE1,BE0),AND(BE0,BE1),OR(BE0,BE1))"
