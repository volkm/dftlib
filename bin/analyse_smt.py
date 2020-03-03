import argparse

from dftlib.analysis.smt import SMTAnalysis

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description='Analyse a DFT via SMT.')
    argument_parser.add_argument('--dft', '-i', help='The path for the dft file in Galileo or JSON encoding', required=True)
    argument_parser.add_argument('--out', '-o', help='The path for the resulting smt file', required=True)

    args = argument_parser.parse_args()

    # Analyse DFT
    smt = SMTAnalysis()
    lower, upper, length = smt.check_eventually_fail(args.dft, args.out)
    print("Bounds: {} - {} (instead of 0 - {})".format(lower, upper, length))
