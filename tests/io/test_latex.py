from helpers.helper import get_example_path

import os

import dftlib.io.parser
import dftlib.io.latex


def test_export_tikz(tmpdir):
    file = get_example_path("json", "all_types.json")
    dft = dftlib.io.parser.parse_dft_json(file)

    tmp_path = os.path.join(tmpdir, "tizk.tex")
    dftlib.io.latex.generate_tikz(dft, tmp_path)

    tmp_file = open(tmp_path, 'r').read().splitlines()
    assert tmp_file[0] == "\\begin{tikzpicture}"
    assert tmp_file[-1] == "\\end{tikzpicture}"
