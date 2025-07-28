dftlib - Python library for dynamic fault tree analysis
=======================================================

[![Docs Badge](https://img.shields.io/badge/docs-latest-blue)](https://volkm.github.io/dftlib/)
[![Build Status](https://github.com/volkm/dftlib/workflows/Build%20Test/badge.svg)](https://github.com/volkm/dftlib/actions)
[![PyPI - Version](https://img.shields.io/pypi/v/dftlib)](https://pypi.org/project/dftlib/)

### Installation
The dftlib Python package can be installed with:
```
pip install dftlib
```

### Features
The dftlib library provides Python support for fault tree analysis, especially dynamic fault trees (DFT).
- Import and export (dynamic) fault trees from the following formats:
  - [Galileo format](https://www.cse.msu.edu/~cse870/Materials/FaultTolerant/manual-galileo.htm#Editing%20in%20the%20Textual%20View), a collection of fault trees is available in the [FFORT collection](https://dftbenchmarks.utwente.nl/ffort/ffort.php).
  - custom JSON format. The JSON format is compatible with the [SAFEST tool](https://www.safest.dgbtek.com/) and the [DFT visualization](https://moves-rwth.github.io/dft-gui/).
  - simple text format of the form `AND(OR(A,B),C)`
- Export fault tree in tikz code for LaTeX. Layouting information from the JSON format is preserved. The export uses the DFT symbols defined in [dft-tikz.tex](resources/latex/dft_tikz.tex). An example template is provided in [resources/latex](resources/latex/template.tex).
- Anonymize fault trees for publication
- Simplify the fault tree structure through graph rewriting. The simplifications rules are in parts based on:
[Junges et al. 'Fault trees on a diet: automated reduction by graph rewriting'](https://doi.org/10.1007/s00165-016-0412-0)
- Analyze DFT via SMT encoding


### Contributors
Main author:
- Matthias Volk

The development of dftlib received significant contributions from:
- Dustin Jungen
