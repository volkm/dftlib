import argparse

import dft_lib.io.parser
import dft_lib.io.export
import dft_lib.transformer.rewriting

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplify a DFT by rewriting.')

    parser.add_argument('--dft', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', help='The path for the saved dft file in JSON encoding', required=True)
    args = parser.parse_args()

    # Read DFT file
    print("Reading {}".format(args.dft))
    dft = dft_lib.io.parser.parse_dft_json(args.dft)
    print(dft)

    # Split FDEPs in DFT
    dft_lib.transformer.rewriting.split_fdeps(dft)

    # Simplify DFT
    dft_lib.transformer.rewriting.simplify_dft(dft)
    print(dft)

    # Save DFT again
    dft_lib.io.export.export_dft_json(dft, args.out)
