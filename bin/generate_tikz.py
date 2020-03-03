import argparse

import dftlib.io.parser
import dftlib.io.latex

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate tikz file visualizing the given DFT.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the generated tikz file', required=True)
    args = parser.parse_args()

    # Read DFT file
    print("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json(args.dft)
    print(dft)

    # Generate tikz file
    dftlib.io.latex.generate_tikz(dft, args.out)

