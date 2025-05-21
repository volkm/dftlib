import itertools
import logging

from dftlib.exceptions.exceptions import DftInvalidArgumentException
from dftlib.transformer.rewrite_rules import RewriteRules

"""
Simplify DFT structure by graph rewriting.
The simplifications is based on the 29 rewrite rules presented in:
Junges, S., Guck, D., Katoen, J.-P., Rensink, A., Stoelinga, M., 2017.
'Fault trees on a diet: automated reduction by graph rewriting'. Form Asp Comp 29, 651–703.
https://doi.org/10.1007/s00165-016-0412-0
"""


def apply_rules(dft, rules):
    """
    Try to apply the given rewrite rules (of "Fault trees on a diet").
    The function stops if either a rule could be applied or no change could be made.
    :param dft: DFT.
    :param rules: Rewrite rules to apply. They are specified as a list of type RewriteRules.
    :return: Tuple (rewrite rule, element) if the rewrite rule could be applied to element. Returns (None, None) if no rule could be applied.
    """
    if RewriteRules.ADD_SINGLE_OR in rules:
        logging.warning("Rule ADD_SINGLE_OR could lead to non-termination")

    for rule in rules:
        # Get function to execute for rule
        func = RewriteRules.get_function(rule)

        # Handle special rules
        if rule == RewriteRules.MERGE_IDENTICAL_GATES:
            # Iterate over all possible combinations of gates
            for elem1, elem2 in itertools.combinations(dft.elements.values(), 2):
                if func(dft, elem1, elem2):
                    return rule, elem1
        elif rule == RewriteRules.TRIM:
            # Try to trim DFT
            if func(dft):
                return rule, None
        else:
            # Default rules: apply function to all elements
            for element in dft.elements.values():
                if func(dft, element):
                    return rule, element

    # No rule could successfully be applied
    return None, None


def simplify_dft_all_rules(dft):
    """
    Simplify DFT by applying all available rewrite rules.
    :param dft: DFT.
    :return: Simplified DFT.
    """
    all_rules = [
        RewriteRules.SPLIT_FDEPS,
        RewriteRules.MERGE_BES,
        RewriteRules.TRIM,
        RewriteRules.REMOVE_DEPENDENCIES_TLE,
        RewriteRules.REMOVE_DUPLICATES,
        RewriteRules.FACTOR_COMMON_CAUSE,
        RewriteRules.MERGE_IDENTICAL_GATES,
        RewriteRules.REMOVE_SINGLE_SUCCESSOR,
        # RewriteRules.ADD_SINGLE_OR, # Could lead to infinite loop by adding new gates
        RewriteRules.FLATTEN_GATE,
        RewriteRules.SUBSUME_GATE,
        RewriteRules.REPLACE_FDEP_BY_OR,
        RewriteRules.REMOVE_SUPERFLUOUS_FDEP,
        RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS,
    ]
    return simplify_dft_rules(dft, all_rules)


def simplify_dft_default_rules(dft):
    """
    Simplify DFT by applying some default rewrite rules.
    :param dft: DFT.
    :return: Simplified DFT.
    """
    default_rules = [RewriteRules.SPLIT_FDEPS, RewriteRules.MERGE_BES, RewriteRules.TRIM, RewriteRules.REMOVE_SINGLE_SUCCESSOR, RewriteRules.FLATTEN_GATE]
    return simplify_dft_rules(dft, default_rules)


def simplify_dft_rules(dft, rules):
    """
    Simplify DFT in place by applying the given rewrite rules of "Fault trees on a diet".
    :param dft: DFT.
    :param rules: Rewrite rules to apply. They are specified as a list of type RewriteRules.
    :return: True iff the DFT changed.
    """
    logging.debug("Starting simplification with rules {} on {}".format(rules, dft))
    logging.debug(dft.verbose_str())

    simplified = False
    while True:
        rule, element = apply_rules(dft, rules)

        if rule is None:
            # No rule could be applied -> terminate
            break

        simplified = True
        if rule == RewriteRules.SPLIT_FDEPS:
            logging.debug("Split FDEP: {}".format(element))
        elif rule == RewriteRules.MERGE_BES:
            logging.debug("Merged BEs under OR: {}".format(element))
        elif rule == RewriteRules.TRIM:
            logging.debug("Trimmed DFT")
        elif rule == RewriteRules.REMOVE_DEPENDENCIES_TLE:
            logging.debug("Removed dependency: {}".format(element))
        elif rule == RewriteRules.REMOVE_DUPLICATES:
            logging.debug("Removed duplicates in gate {}".format(element))
        elif rule == RewriteRules.FACTOR_COMMON_CAUSE:
            logging.debug("Factored out common cause in gate {}".format(element))
        elif rule == RewriteRules.MERGE_IDENTICAL_GATES:
            logging.debug("Merged gate {}".format(element))
        elif rule == RewriteRules.REMOVE_SINGLE_SUCCESSOR:
            logging.debug("Removed gate with single successor: {}".format(element))
        elif rule == RewriteRules.ADD_SINGLE_OR:
            logging.debug("Added single OR: {}".format(element))
        elif rule == RewriteRules.FLATTEN_GATE:
            logging.debug("Flattened gate: {}".format(element))
        elif rule == RewriteRules.SUBSUME_GATE:
            logging.debug("Subsumed gate: {}".format(element))
        elif rule == RewriteRules.REPLACE_FDEP_BY_OR:
            logging.debug("Replaced FDEP by OR: {}".format(element))
        elif rule == RewriteRules.REMOVE_SUPERFLUOUS_FDEP:
            logging.debug("Removed superfluous FDEP: {}".format(element))
        elif rule == RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS:
            logging.debug("Removed FDEP with successors: {}".format(element))
        else:
            raise DftInvalidArgumentException("Rewrite rule {} not known".format(rule))

        # Print new DFT
        logging.debug(dft.verbose_str())

    assert not dft.is_cyclic()
    return simplified
