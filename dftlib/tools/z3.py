from dftlib.exceptions.exceptions import ToolNotFound, DftInvalidArgumentException

try:
    import z3 as _z3
except ImportError:
    _has_z3 = False
else:
    _has_z3 = True


def requires_z3(func):
    """
    Decorator to check whether z3 is available
    """

    def wrapper(*args, **kwargs):
        if _has_z3:
            return func(*args, **kwargs)
        else:
            raise ToolNotFound("z3 is required for this functionality.")

    return wrapper


@requires_z3
class Z3:
    """
    Class wrapping Z3
    """

    def __init__(self):
        """
        Constructor.
        """
        self.solver = _z3.Solver()

    def check(self, lines):
        constraints = _z3.parse_smt2_string("\n".join(lines))
        result = self.solver.check(constraints)
        if str(result) == "unsat":
            return False
        elif str(result) == "sat":
            return True
        else:
            raise DftInvalidArgumentException("Unknown output of z3 '" + str(result) + "'")
