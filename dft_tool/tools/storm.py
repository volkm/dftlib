from pathlib import Path
import os
import re
import math

from dft_tool.utility.os_functions import run_tool


class Storm:
    """
    Class wrapping the storm model checker CLI.
    """

    def __init__(self, binary):
        """
        Constructor.
        :param binary: Path to storm-dft binary.
        """
        self.binary = binary

    def convert_to_json(self, file, tmpjson):
        args = [self.binary, '-dft', file, '--export-json', tmpjson]
        outputstr = run_tool(args, True)
        return outputstr

    def analyse_with_smt(self, file, outfile):
        args = [self.binary, '-dft', file, '--dft:smt']
        _ = run_tool(args, True)

        smt_file = Path("test.smt2")
        assert smt_file.is_file()

        with open(smt_file, "r") as f:
            smtlib = f.read()

        lines = smtlib.splitlines()
        last_line = lines[-1]
        assert last_line == "(check-sat)"
        last_assert = lines[-2]
        match = re.search(r"\(assert \(= t_(.*) (.*)\)\)", last_assert)
        assert match
        toplevel = match.group(1)
        length = int(match.group(2))

        with open(outfile, 'w') as fout:
            fout.write("\n".join(lines[:-2]))

        # Check upper bound
        # All basic failures should lead to complete failure
        sat = self.check_threshold(lines[:-2], length, "=", toplevel, outfile)
        assert not sat

        # Refine
        l, u = 0, length
        while l != u:
            threshold = math.ceil((l + u) / 2)
            sat = self.check_threshold(lines[:-2], threshold, ">=", toplevel, outfile)
            if sat:
                l = threshold
            else:
                u = threshold - 1
        upper = l

        # Check lower bound
        # No basic failures should lead to no failure
        sat = self.check_threshold(lines[0:-2], 0, "=", toplevel, outfile)
        assert not sat

        # Refine
        l, u = 0, upper
        while l != u:
            threshold = math.floor((l + u) / 2)
            sat = self.check_threshold(lines[:-2], threshold, "<=", toplevel, outfile)
            if sat:
                u = threshold
            else:
                l = threshold + 1
        lower = l

        return lower, upper, length

    def check_threshold(self, lines, threshold, comparison, toplevel, out):
        tmp_file = "tmp.smt2"
        with open(out, 'a') as fout:
            with open(tmp_file, 'w') as ftmp:
                ftmp.write("\n".join(lines))
                ftmp.write("\n(assert ({} t_{} {}))".format(comparison, toplevel, threshold))
                ftmp.write("\n(check-sat)")

            fout.write("\n(push)")
            fout.write("\n(assert ({} t_{} {}))".format(comparison, toplevel, threshold))
            fout.write("\n(check-sat)")
            fout.write("\n(pop)")

            print("Threshold: {}".format(threshold))
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
