import argparse
import logging

import dftlib.io.export_txt
import dftlib.io.parser
import dftlib.transformer.simplifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a DFT as textual description.")

    parser.add_argument("--dft", "-i", help="The path for the dft file", required=True)
    parser.add_argument("--out", "-o", help="The path for the saved dft file as textual description", required=True)
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Save DFT again
    dftlib.io.export_txt.export_dft_file(dft, args.out)
    logging.info("Exported DFT in textual description.")
