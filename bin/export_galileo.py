import argparse
import logging

import dftlib.io.export
import dftlib.io.parser
import dftlib.transformer.simplifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export a DFT into Galileo format.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the saved dft file in Galileo format', required=True)
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json_file(args.dft)
    logging.info(dft)

    # Save DFT again
    dftlib.io.export.export_dft_galileo(dft, args.out)
    logging.info("Exported DFT in Galileo format.")
