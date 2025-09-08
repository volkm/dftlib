#!/usr/bin/env python

import argparse
import logging

import dftlib.io.export_json
import dftlib.io.parser
import dftlib.transformer.simplifier as simplifier


def main():
    parser = argparse.ArgumentParser(description="Simplify a DFT by rewriting.")

    parser.add_argument("--dft", "-i", help="The path for the dft file", required=True)
    parser.add_argument("--out", "-o", help="The path for the simplified dft file in JSON encoding", required=True)
    parser.add_argument("--all-rules", "-a", help="Use all rewriting rules", action="store_true")
    parser.add_argument("--verbose", "-v", help="print more output", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.DEBUG if args.verbose else logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_file(args.dft)
    logging.info(dft)

    # Simplify DFT
    if args.all_rules:
        rules = simplifier.get_all_rules()
    else:
        rules = simplifier.get_default_rules()
    simplified = simplifier.simplify_dft_rules(dft, rules)

    if simplified:
        logging.info("DFT was simplified")
        logging.info(dft)
    else:
        logging.info("DFT was not simplified")

    # Save DFT again
    dftlib.io.export_json.export_dft_file(dft, args.out)


if __name__ == "__main__":
    main()
