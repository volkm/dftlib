import os
import re
import math

import dftlib._config as config
from dftlib.utility.os_functions import run_tool
from dftlib.exceptions.exceptions import ToolNotFound


class Storm:
    """
    Class wrapping the storm model checker CLI.
    """

    def __init__(self):
        """
        Constructor.
        """
        if config.has_storm_dft:
            self.binary = config.storm_path
        else:
            raise ToolNotFound("Path of binary 'storm-dft' not specified.")

    def convert_to_json(self, file, out_file):
        """
        Convert galileo file to json file.
        :param file: File.
        :param out_file: Output file.
        :return: JSON string of the DFT.
        """
        args = [self.binary, '-dft', file, '--export-json', out_file]
        run_tool(args, True)

    def analyse_with_smt(self, file, smt_file):
        """
        Analyse DFT via SMT.
        :param file: Input file.
        :param smt_file: Output SMT file.
        :return: Tuple (lower bound, upper bound, number of failable BEs)
        """
        args = [self.binary, '-dft', file, '--export-smt', smt_file]
        run_tool(args, True)

        with open(smt_file, "r") as f:
            smtlib = f.read()

        lines = smtlib.splitlines()
        assert lines[-1] == "(check-sat)"
        match = re.search(r"\(assert \(= t_(.*) (.*)\)\)", lines[-2])
        assert match
        toplevel = match.group(1)
        length = int(match.group(2))

        lines = ["(set-logic QF_UFIDL)", "(set-option :smt.arith.solver 3)"] + lines

        with open(smt_file, 'w') as fout:
            fout.write("\n".join(lines[:-2]))

        # Check upper bound
        # All basic failures should lead to complete failure
        sat = self.check_threshold(lines[:-2], length, length, toplevel, smt_file)
        if sat:
            print("IS FAILSAFE")
            upper = length
        else:
            # Refine
            l, u = 0, length
            while l != u:
                threshold = math.ceil((l + u) / 2)
                sat = self.check_threshold(lines[:-2], threshold, u, toplevel, smt_file)
                if sat:
                    l = threshold
                else:
                    u = threshold - 1
            upper = l

        # Check lower bound
        # No basic failures should lead to no failure
        sat = self.check_threshold(lines[0:-2], 0, 0, toplevel, smt_file)
        assert not sat

        # Refine
        l, u = 0, upper
        while l != u:
            threshold = math.floor((l + u) / 2)
            sat = self.check_threshold(lines[:-2], l, threshold, toplevel, smt_file)
            if sat:
                u = threshold
            else:
                l = threshold + 1
        lower = l

        return lower, upper, length

    def check_threshold(self, lines, threshold_l, threshold_u, toplevel, out):
        tmp_file = "tmp.smt2"
        assert threshold_l <= threshold_u
        if threshold_l == threshold_u:
            comparison = "= t_{} {}".format(toplevel, threshold_l)
        else:
            comparison = "and (>= t_{0} {1}) (<= t_{0} {2})".format(toplevel, threshold_l, threshold_u)

        with open(out, 'a') as fout:
            with open(tmp_file, 'w') as ftmp:
                ftmp.write("\n".join(lines))
                ftmp.write("\n(assert ({}))".format(comparison))
                ftmp.write("\n(check-sat)")

            fout.write("\n(push)")
            fout.write("\n(assert ({}))".format(comparison))
            fout.write("\n(check-sat)")
            fout.write("\n(pop)")

            # print("Threshold {}".format(threshold))
            args_z3 = ['z3', tmp_file]
            outputstr = run_tool(args_z3, True)
            os.remove(tmp_file)
            if outputstr == 'unsat':
                # All sequences lead to failure
                fout.write("\n; expect unsat")
                return False
            elif outputstr == 'sat':
                # At least one sequence does not lead to failure
                fout.write("\n; expect sat")
                return True
            else:
                print("UNKNOWN output '" + outputstr + "'")
                return None
