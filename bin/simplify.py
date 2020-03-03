import argparse

import dftlib.io.parser
import dftlib.io.export
import dftlib.transformer.rewriting
import dftlib.transformer.trimming

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplify a DFT by rewriting.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the saved dft file in JSON encoding', required=True)
    args = parser.parse_args()

    # Read DFT file
    print("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json(args.dft)
    print(dft)

    # Split FDEPs in DFT
    dftlib.transformer.rewriting.split_fdeps(dft)

    changed = True
    while changed:
        no_elements_before = len(dft.elements)
        # Simplify DFT
        dftlib.transformer.rewriting.simplify_dft(dft, rules=["1", "2", "5"])
        print(dft)

        dftlib.transformer.trimming.trim(dft)
        print(dft)

        no_elements_after = len(dft.elements)
        changed = (no_elements_before != no_elements_after)

    # Save DFT again
    dftlib.io.export.export_dft_json(dft, args.out)
