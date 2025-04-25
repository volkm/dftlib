import os

from helpers.helper import get_example_path

import dftlib.io.latex
import dftlib.io.parser


def test_export_tikz(tmpdir):
    file = get_example_path("json", "all_gates.json")
    dft = dftlib.io.parser.parse_dft_json_file(file)

    tmp_path = os.path.join(tmpdir, "tizk.tex")
    dftlib.io.latex.generate_tikz(dft, tmp_path)

    tmp_file = open(tmp_path, "r").read().splitlines()
    assert tmp_file[0] == "\\begin{tikzpicture}"
    assert tmp_file[-1] == "\\end{tikzpicture}"
