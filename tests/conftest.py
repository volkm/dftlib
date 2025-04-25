import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "helpers"))

# Skip functionality which is not available
from dftlib.tools.storm import _has_storm
from dftlib.tools.stormpy import _has_stormpy
from dftlib.tools.z3 import _has_z3

storm = pytest.mark.skipif(not _has_storm, reason="Storm not available")
stormpy = pytest.mark.skipif(not _has_stormpy, reason="stormpy not available")
z3 = pytest.mark.skipif(not _has_z3, reason="z3-solver not available")
