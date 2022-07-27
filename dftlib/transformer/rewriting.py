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
    REPLACE_FDEP_BY_OR = 24
    REMOVE_SUPERFLUOUS_FDEP = 25  # also 26
    REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS = 27  # also 28


def simplify_dft(dft, rules=None):
    """
    Simplify DFT by applying the given rewrite rules of "Fault trees on a diet".
    :param dft: DFT.
    :param rules: Rewrite rules to apply. They are specified as a list of type RewriteRules.
    :return: Simplified DFT.
    """
    if rules is None:
        # Set default rewrite rules
        rules = [RewriteRules.SPLIT_FDEPS, RewriteRules.MERGE_ORS, RewriteRules.MERGE_BES, RewriteRules.REMOVE_SINGLE_SUCCESSOR]

    # Binary FDEPs are required for several rewrite rules
    if RewriteRules.SPLIT_FDEPS in rules:
        rewrite_rules.split_fdeps(dft)

    changed = True
    while changed:
        for _, element in dft.elements.items():
            if RewriteRules.MERGE_ORS in rules:
                changed = rewrite_rules.try_merge_or(dft, element)
                if changed:
                    break
            if RewriteRules.MERGE_BES in rules:
                changed = rewrite_rules.try_merge_bes_in_or(dft, element)
                if changed:
                    break
            if RewriteRules.REMOVE_DEPENDENCIES_TLE in rules:
                changed = rewrite_rules.try_remove_dependencies(dft, element)
                if changed:
                    break
            # This rule could always be applied
            # if RewriteRules.ADD_SINGLE_OR in rules:
            #    changed = rewrite_rules.add_or_as_predecessor(dft, element)
            #    if changed:
            #        break
            if RewriteRules.MERGE_IDENTICAL_GATES in rules:
                for _, element2 in dft.elements.items():
                    changed = rewrite_rules.try_merge_identical_gates(dft, element, element2)
                    if changed:
                        break
                if changed:
                    break
            if RewriteRules.REMOVE_SINGLE_SUCCESSOR in rules:
                changed = rewrite_rules.try_remove_gates_with_one_successor(dft, element)
                if changed:
                    break
            if RewriteRules.REPLACE_FDEP_BY_OR in rules:
                changed = rewrite_rules.try_replace_fdep_by_or(dft, element)
                if changed:
                    break
            if RewriteRules.REMOVE_SUPERFLUOUS_FDEP in rules:
                changed = rewrite_rules.try_remove_superfluous_fdep(dft, element)
                if changed:
                    break
            if RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS in rules:
                changed = rewrite_rules.try_remove_fdep_successors(dft, element)
                if changed:
                    break

    return dft
