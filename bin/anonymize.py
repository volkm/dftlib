import argparse
import logging

import dftlib.io.export_json
import dftlib.io.parser
import dftlib.transformer.anonymizer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform the given DFT into an anonymized DFT.")

    parser.add_argument("--dft", help="The path for the dft file", required=True)
    parser.add_argument("--out", help="The path for the anonymous dft file in JSON encoding", required=True)
    parser.add_argument("--grid", help="Position the elements in a grid layout", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Make anonymous
    dftlib.transformer.anonymizer.make_anonymous(dft, args.grid)

    # Save DFT again
    dftlib.io.export_json.export_dft_file(dft, args.out)
    logging.info("Anonymized DFT.")
