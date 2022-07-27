import argparse
import logging

import dftlib.io.export
import dftlib.io.parser
import dftlib.transformer.rewriting as rewriting
import dftlib.transformer.trimming as trimming

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simplify a DFT by rewriting.')

    parser.add_argument('--dft', '-i', help='The path for the dft file in JSON encoding', required=True)
    parser.add_argument('--out', '-o', help='The path for the saved dft file in JSON encoding', required=True)
    parser.add_argument('--all-rules', '-a', help='Use all rewriting rules', action="store_true")
    parser.add_argument('--verbose', '-v', help='print more output', action="store_true")
    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG if args.verbose else logging.INFO)

    # Read DFT file
    logging.info("Reading {}".format(args.dft))
    dft = dftlib.io.parser.parse_dft_json_file(args.dft)
    logging.info(dft)

    simplified = False
    while True:
        # Simplify DFT
        if args.all_rules:
            rewritten = rewriting.simplify_dft_all_rules(dft)
        else:
            rewritten = rewriting.simplify_dft(dft)

        if rewritten:
            logging.info("DFT was rewritten")
            logging.info(dft)
            simplified = True

        trimmed = trimming.trim(dft)
        if trimmed:
            logging.info("DFT was trimmed")
            logging.info(dft)
            simplified = True

        if not rewritten and not trimmed:
            break

    if not simplified:
        logging.info("DFT was not simplified")

    # Save DFT again
    dftlib.io.export.export_dft_json(dft, args.out)
