import argparse
import logging

import dftlib.io.latex
import dftlib.io.parser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tikz file visualizing the given DFT.")

    parser.add_argument("--dft", "-i", help="The path for the dft file", required=True)
    parser.add_argument("--out", "-o", help="The path for the generated tikz file", required=True)
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Generate tikz file
    dftlib.io.latex.generate_tikz(dft, args.out)
    logging.info("Generated tikz file.")
