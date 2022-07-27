import argparse
import logging

import dftlib.io.export
import dftlib.io.parser
import dftlib.transformer.trimming
from dftlib.transformer.rewriting import RewriteRules, simplify_dft

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplify a DFT by rewriting.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the saved dft file in JSON encoding', required=True)
    parser.add_argument('--verbose', '-v', help='print more output', action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json_file(args.dft)
    logging.info(dft)

    changed = True
    while changed:
        no_elements_before = len(dft.elements)
        # Simplify DFT
        simplify_dft(dft)
        logging.debug(dft)

        dftlib.transformer.trimming.trim(dft)
        logging.debug(dft)

        no_elements_after = len(dft.elements)
        changed = (no_elements_before != no_elements_after)
    logging.info("Simplified DFT")
    logging.info(dft)

    # Save DFT again
    dftlib.io.export.export_dft_json(dft, args.out)
