import math

from dftlib.io.parser import parse_dft_galileo
from dftlib.tools.storm import Storm
from dftlib.tools.z3 import Z3


class SMTAnalysis:
    """
    Analysis using SMT encoding.
    """

    def __init__(self):
        self.storm = Storm()
        self.z3 = Z3()

    def check_eventually_fail(self, file, smt_file):
        """
        Check that the DFT will eventually fail using SMT solvers.
        :param file: Input DFT file in Galileo format.
        :param smt_file: Output file in SMT format.
        #:return: Tuple (lower bound, upper bound, number of failable BEs)
        """
        # Generate SMT encoding with Storm
        smt_encoding = self.storm.export_smt(file)
        lines = smt_encoding.splitlines()
        assert lines[-1] == "(check-sat)"
        # Get top level event by converting to JSON
        dft = parse_dft_galileo(file)
        assert dft.top_level_element
        toplevel = dft.top_level_element.name
        # Get maximal length as number of BEs
        length = dft.number_of_be()

        lines = ["(set-logic QF_UFIDL)", "(set-option :smt.arith.solver 3)"] + lines
        # base_encoding = lines[:-2]
        base_encoding = lines[:-1]

        # Write base encoding to file
        with open(smt_file, 'w') as f:
            f.write("\n".join(base_encoding))

        # Check upper bound
        # All BE failures should lead to complete failure
        sat = self.check_threshold(base_encoding, length, length, toplevel, smt_file)
        if sat:
            # DFT is failsafe
            upper = length
        else:
            # Refine and find upper bound (minimal number of BEs which always leads to a DFT failure)
            l, u = 0, length
            while l != u:
                threshold = math.ceil((l + u) / 2)
                sat = self.check_threshold(base_encoding, threshold, u, toplevel, smt_file)
                if sat:
                    l = threshold
                else:
                    u = threshold - 1
            upper = l

        # Check lower bound
        # No BE failures should lead to no failure
        sat = self.check_threshold(base_encoding, 0, 0, toplevel, smt_file)
        assert not sat

        # Refine and find lower bound (minimal number of BEs which leads to a DFT failure)
        l, u = 0, upper
        while l != u:
            threshold = math.floor((l + u) / 2)
            sat = self.check_threshold(base_encoding, l, threshold, toplevel, smt_file)
            if sat:
                u = threshold
            else:
                l = threshold + 1
        lower = l

        return lower, upper, length

    def check_threshold(self, lines, threshold_l, threshold_u, toplevel, smt_file):
        assert threshold_l <= threshold_u
        if threshold_l == threshold_u:
            comparison = "= t_{} {}".format(toplevel, threshold_l)
        else:
            comparison = "and (>= t_{0} {1}) (<= t_{0} {2})".format(toplevel, threshold_l, threshold_u)

        # Add assertions to output file
        with open(smt_file, 'a') as f:
            f.write("\n(push)")
            f.write("\n(assert ({}))".format(comparison))
            f.write("\n(check-sat)")
            f.write("\n(pop)")

        lines_check = lines + ["(assert ({}))".format(comparison), "(check-sat)"]
        return self.z3.check(lines_check)
