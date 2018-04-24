import argparse

import dft_tool.io.parser
import dft_tool.io.export
import dft_tool.transformer.rewriting

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplify a DFT by rewriting.')

    parser.add_argument('--dft', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', help='The path for the saved dft file in JSON encoding', required=True)
    args = parser.parse_args()

    # Read DFT file
    print("Reading {}".format(args.dft))
    dft = dft_tool.io.parser.parse_dft_json(args.dft)
    print(dft)

    # Simplify DFT
    dft_tool.transformer.rewriting.simplify_dft(dft)
    print(dft)

    # Save DFT again
    dft_tool.io.export.export_dft_json(dft, args.out)
