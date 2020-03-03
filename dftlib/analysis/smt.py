from dftlib.tools.storm import Storm


class SMTAnalysis:
    """
    Analysis using SMT encoding.
    """

    def __init__(self):
        self.storm = Storm()

    def check_eventually_fail(self, file, smt_file):
        """
        Check that the DFT will fail eventually using SMT solvers.
        :param file: Input DFT file.
        :param smt_file: Output file in SMT format.
        :return: True iff the DFT will fail eventually.
        """
        return self.storm.analyse_with_smt(file, smt_file)
