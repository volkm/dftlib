from helpers.helper import get_example_path

import os

import dftlib.io.parser
import dftlib.io.export


def test_export_galileo(tmpdir):
    file = get_example_path("simplify", "HECS_re.json")
    dft = dftlib.io.parser.parse_dft_json(file)

    tmp_path = os.path.join(tmpdir, "hecs.dft")
    dftlib.io.export.export_dft_galileo(dft, tmp_path)

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
        '"FDEP_26" fdep "MIU2" "M4";'
    ]

    tmp_file = open(tmp_path, 'r').read().splitlines()
    for i in range(0, len(tmp_file)):
        assert tmp_file[i] == expected_lines[i]
