***********************
Features
***********************

The dftlib library provides Python support for fault tree analysis, especially dynamic fault trees (DFT).

Import/Export
=============

The library supports the import and export of (dynamic) fault trees from the following formats.

Galileo format
--------------
The Galileo format was originally introduced by the `Galileo DFT tool <https://www.cse.msu.edu/~cse870/Materials/FaultTolerant/manual-galileo.htm>`_.
The original format is described in the `Galileo manual <https://www.cse.msu.edu/~cse870/Materials/FaultTolerant/manual-galileo.htm#Editing%20in%20the%20Textual%20View>`_ and an extension version is described on the `FFORT website <https://dftbenchmarks.utwente.nl/ffort/galileo.html>`_.
A collection of fault trees in the Galileo format is available in the `FFORT collection <https://dftbenchmarks.utwente.nl/ffort/ffort.php>`_.

JSON format
-----------
The library support a custom JSON format describing the DFT elements.
The JSON format is compatible with the `DFT visualization <https://moves-rwth.github.io/dft-gui/>`_, the `Storm model checker <https://www.stormchecker.org/>`_ and the `SAFEST tool <https://www.safest.dgbtek.com/>`_.

Text format
-----------
The library also supports a simple text format of the following form::

  AND(OR(A,B),C)

All three formats can be imported and exported with dftlib.
Furthermore, export in anonymized form is also possible.
This export anonymizes event names such that publication without confidential information is possible.

LaTeX generation
================
dftlib supports exporting fault trees as tikz code for LaTeX.
When using the JSON format, the layouting information from the JSON format is preserved in the layout of the tikz code.
The tikz export uses the DFT symbols defined in `dft-tikz.tex <https://github.com/volkm/dftlib/blob/main/resources/latex/dft_tikz.tex>`_.
An example template is provided in `resources/latex <https://github.com/volkm/dftlib/blob/main/resources/latex/template.tex>`_.

Fault tree simplification
=========================
The fault tree structure can be simplified through graph rewriting.
The simplifications rules are in parts based on `Junges et al. 'Fault trees on a diet: automated reduction by graph rewriting' <https://doi.org/10.1007/s00165-016-0412-0>`_.


Analysis
========
The (dynamic) fault trees can be analysed with the `Storm model checker <https://www.stormchecker.org/>`_ as described `here <https://www.stormchecker.org/documentation/usage/running-storm-on-dfts.html>`_.
The easiest approach is using the `stormpy <https://moves-rwth.github.io/stormpy/>`_ Python bindings for Storm.
The steps for fault tree analysis are described in the `stormpy documentation <https://moves-rwth.github.io/stormpy/doc/dfts.html>`_.

dftlib also supports analysis of DFT via encoding in satisfiability modulo theories (SMT).
