import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))

# Skip functionality which is not available
from dftlib.tools.stormpy import _has_stormpy

stormpy = pytest.mark.skipif(not _has_stormpy, reason="stormpy not available")
