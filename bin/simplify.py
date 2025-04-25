import argparse
import logging

import dftlib.io.export_json
import dftlib.io.parser
import dftlib.transformer.simplifier as rewriting

if __name__ == "__main__":
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
        simplified = rewriting.simplify_dft_all_rules(dft)
    else:
        simplified = rewriting.simplify_dft_default_rules(dft)

    if simplified:
        logging.info("DFT was simplified")
        logging.info(dft)
    else:
        logging.info("DFT was not simplified")

    # Save DFT again
    dftlib.io.export_json.export_dft_file(dft, args.out)
