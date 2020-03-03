import argparse

import dftlib.io.parser
import dftlib.io.export
import dftlib.transformer.rewriting

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Export a DFT into Galileo format.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the saved dft file in Galileo format', required=True)
    args = parser.parse_args()

    # Read DFT file
    print("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json(args.dft)
    print(dft)

    # Save DFT again
    dftlib.io.export.export_dft_galileo(dft, args.out)
