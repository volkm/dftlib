import argparse
import logging

import dftlib.io.export_json
import dftlib.io.parser
import dftlib.transformer.simplifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export a DFT into JSON format.")

    parser.add_argument("--dft", "-i", help="The path for the dft file", required=True)
    parser.add_argument("--out", "-o", help="The path for the saved dft file in JSON format", required=True)
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Save DFT again
    dftlib.io.export_json.export_dft_file(dft, args.out)
    logging.info("Exported DFT in JSON format.")
