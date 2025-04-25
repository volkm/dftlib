import argparse
import logging

import dftlib.io.parser
from dftlib.analysis.smt import SMTAnalysis

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description="Analyse a DFT via SMT.")
    argument_parser.add_argument("--dft", "-i", help="The path for the dft file", required=True)
    argument_parser.add_argument("--out", "-o", help="The path for the resulting smt file", required=True)
    args = argument_parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Analyse DFT
    smt = SMTAnalysis()
    lower, upper, length = smt.check_eventually_fail(dft, args.out)
    logging.info("Bounds: {} - {} (instead of 0 - {})".format(lower, upper, length))
