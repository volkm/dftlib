import logging
from enum import Enum

from dftlib.transformer import rewrite_rules

"""
Simplify DFT structure by graph rewriting.
The simplifications is based on the 29 rewrite rules presented in:
Junges, S., Guck, D., Katoen, J.-P., Rensink, A., Stoelinga, M., 2017.
'Fault trees on a diet: automated reduction by graph rewriting'. Form Asp Comp 29, 651–703.
https://doi.org/10.1007/s00165-016-0412-0
"""


class RewriteRules(Enum):
    """
    Rewrite rules.
    Numbers < 30 correspond to the rewrite rule number in "Fault trees on a diet".
    """
    SPLIT_FDEPS = 30
    MERGE_BES = 31
    MERGE_ORS = 32
    REMOVE_DEPENDENCIES_TLE = 32
    MERGE_IDENTICAL_GATES = 2
    REMOVE_SINGLE_SUCCESSOR = 3
    ADD_SINGLE_OR = 4
    FLATTEN_GATE = 5
    REPLACE_FDEP_BY_OR = 24
    REMOVE_SUPERFLUOUS_FDEP = 25  # also 26
    REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS = 27  # also 28


def simplify_dft_all_rules(dft):
    """
    Simplify DFT by applying all available rewrite rules.
    :param dft: DFT.
    :return: Simplified DFT.
    """
    all_rules = [
        RewriteRules.SPLIT_FDEPS,
        RewriteRules.MERGE_BES,
        RewriteRules.MERGE_ORS,
        RewriteRules.REMOVE_DEPENDENCIES_TLE,
        RewriteRules.MERGE_IDENTICAL_GATES,
        RewriteRules.REMOVE_SINGLE_SUCCESSOR,
        RewriteRules.ADD_SINGLE_OR,
        RewriteRules.FLATTEN_GATE,
        RewriteRules.REPLACE_FDEP_BY_OR,
        RewriteRules.REMOVE_SUPERFLUOUS_FDEP,
        RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS
    ]
    return simplify_dft_rules(dft, all_rules)


def simplify_dft(dft):
    """
    Simplify DFT by applying the default rewrite rules.
    :param dft: DFT.
    :return: Simplified DFT.
    """
    default_rules = [
        RewriteRules.SPLIT_FDEPS,
        RewriteRules.MERGE_ORS,
        RewriteRules.MERGE_BES,
        RewriteRules.REMOVE_SINGLE_SUCCESSOR
    ]
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
    # Binary FDEPs are required for several rewrite rules
    if RewriteRules.SPLIT_FDEPS in rules:
        changed = rewrite_rules.split_fdeps(dft)
        if changed:
            logging.debug("Split some dependencies")
            logging.debug(dft.verbose_str())
    simplified = changed

    while True:
        changed = False
        for _, element in dft.elements.items():
            if RewriteRules.MERGE_BES in rules:
                changed = rewrite_rules.try_merge_bes_in_or(dft, element)
                if changed:
                    logging.debug("Merged BEs under OR: {}".format(element))
                    break
            if RewriteRules.MERGE_ORS in rules:
                changed = rewrite_rules.try_merge_or(dft, element)
                if changed:
                    logging.debug("Merged OR: {}".format(element))
                    break
            if RewriteRules.REMOVE_DEPENDENCIES_TLE in rules:
                changed = rewrite_rules.try_remove_dependencies(dft, element)
                if changed:
                    logging.debug("Removed dependency: {}".format(element))
                    break
            if RewriteRules.MERGE_IDENTICAL_GATES in rules:
                for _, element2 in dft.elements.items():
                    changed = rewrite_rules.try_merge_identical_gates(dft, element, element2)
                    if changed:
                        break
                if changed:
                    logging.debug("Merged gates {} and {}".format(element, element2))
                    break
            if RewriteRules.REMOVE_SINGLE_SUCCESSOR in rules:
                changed = rewrite_rules.try_remove_gates_with_one_successor(dft, element)
                if changed:
                    logging.debug("Removed gate with single successor: {}".format(element))
                    break
                # This rule could always be applied
                # if RewriteRules.ADD_SINGLE_OR in rules:
                #    changed = rewrite_rules.add_or_as_predecessor(dft, element)
                #    if changed:
                #        break
            if RewriteRules.FLATTEN_GATE in rules:
                changed = rewrite_rules.try_flatten_gate(dft, element)
                if changed:
                    logging.debug("Flattened gate: {}".format(element))
                    break
            if RewriteRules.REPLACE_FDEP_BY_OR in rules:
                changed = rewrite_rules.try_replace_fdep_by_or(dft, element)
                if changed:
                    logging.debug("Replaced FDEP by OR: {}".format(element))
                    break
            if RewriteRules.REMOVE_SUPERFLUOUS_FDEP in rules:
                changed = rewrite_rules.try_remove_superfluous_fdep(dft, element)
                if changed:
                    logging.debug("Removed superfluous FDEP: {}".format(element))
                    break
            if RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS in rules:
                changed = rewrite_rules.try_remove_fdep_successors(dft, element)
                if changed:
                    logging.debug("Removed FDEP with successors: {}".format(element))
                    break
        if changed:
            logging.debug("Changed DFT")
            logging.debug(dft.verbose_str())
            simplified = True
        else:
            break
    return simplified
