from dftlib.tools.storm import Storm


class SMTAnalysis:
    """
    Analysis using SMT encoding.
    """

    def check_eventually_fail(self, file, outfile):
        """
        Check that the DFT will fail eventually using SMT solvers.
        :param file: File.
        :return: True iff the DFT will fail eventually.
        """
        storm = Storm()
        return storm.analyse_with_smt(file, outfile)
