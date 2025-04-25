import math
import tempfile

import dftlib.io.export_galileo
from dftlib.tools.storm import Storm
from dftlib.tools.z3 import Z3


class SMTAnalysis:
    """
    Analysis using SMT encoding.
    """

    def __init__(self):
        self.storm = Storm()
        self.z3 = Z3()

    def check_eventually_fail(self, dft, smt_file):
        """
        Check that the DFT will eventually fail using SMT solvers.
        :param dft: DFT.
        :param smt_file: Output file in SMT format.
        #:return: Tuple (lower bound, upper bound, number of failable BEs)
        """
        smt_encoding = ""
        with tempfile.NamedTemporaryFile() as tmp_file:
            dftlib.io.export_galileo.export_dft_file(dft, tmp_file.name)
            # Generate SMT encoding with Storm
            smt_encoding = self.storm.export_smt(tmp_file.name)
        lines = smt_encoding.splitlines()
        assert lines[-1] == "(check-sat)"
        assert dft.top_level_element
        toplevel = dft.top_level_element.name
        # Get maximal length as number of BEs
        length = dft.number_of_be()

        lines = ["(set-logic QF_UFIDL)", "(set-option :smt.arith.solver 3)"] + lines
        # base_encoding = lines[:-2]
        base_encoding = lines[:-1]

        # Write base encoding to file
        with open(smt_file, "w") as f:
            f.write("\n".join(base_encoding))

        # Check upper bound
        # All BE failures should lead to complete failure
        sat = self.check_threshold(base_encoding, length, length, toplevel, smt_file)
        if sat:
            # DFT is failsafe
            upper = length
        else:
            # Refine and find upper bound (minimal number of BEs which always leads to a DFT failure)
            l_up, u_up = 0, length
            while l_up != u_up:
                threshold = math.ceil((l_up + u_up) / 2)
                sat = self.check_threshold(base_encoding, threshold, u_up, toplevel, smt_file)
                if sat:
                    l_up = threshold
                else:
                    u_up = threshold - 1
            upper = l_up

        # Check lower bound
        # No BE failures should lead to no failure
        sat = self.check_threshold(base_encoding, 0, 0, toplevel, smt_file)
        assert not sat

        # Refine and find lower bound (minimal number of BEs which leads to a DFT failure)
        l_low, u_low = 0, upper
        while l_low != u_low:
            threshold = math.floor((l_low + u_low) / 2)
            sat = self.check_threshold(base_encoding, l_low, threshold, toplevel, smt_file)
            if sat:
                u_low = threshold
            else:
                l_low = threshold + 1
        lower = l_low

        return lower, upper, length

    def check_threshold(self, lines, threshold_l, threshold_u, toplevel, smt_file):
        assert threshold_l <= threshold_u
        if threshold_l == threshold_u:
            comparison = "= t_{} {}".format(toplevel, threshold_l)
        else:
            comparison = "and (>= t_{0} {1}) (<= t_{0} {2})".format(toplevel, threshold_l, threshold_u)

        # Add assertions to output file
        with open(smt_file, "a") as f:
            f.write("\n(push)")
            f.write("\n(assert ({}))".format(comparison))
            f.write("\n(check-sat)")
            f.write("\n(pop)")

        lines_check = lines + ["(assert ({}))".format(comparison), "(check-sat)"]
        return self.z3.check(lines_check)
