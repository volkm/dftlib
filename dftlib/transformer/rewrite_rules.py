from enum import Enum

import dftlib.storage.dft_gates as dft_gates
import dftlib.transformer.trimming as trimming
import dftlib.utility.numbers as numbers
from dftlib.exceptions.exceptions import DftInvalidArgumentException

"""
Rewrite rules for DFT simplification.
The rules are in parts based on:
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
    TRIM = 32
    REMOVE_DEPENDENCIES_TLE = 33
    REMOVE_DUPLICATES = 34
    FACTOR_COMMON_CAUSE = 35
    MERGE_IDENTICAL_GATES = 2
    REMOVE_SINGLE_SUCCESSOR = 3
    ADD_SINGLE_OR = 4
    FLATTEN_GATE = 5
    SUBSUME_GATE = 8  # also 9
    REPLACE_FDEP_BY_OR = 24
    REMOVE_SUPERFLUOUS_FDEP = 25  # also 26
    REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS = 27  # also 28

    @classmethod
    def get_function(cls, rule):
        if rule == RewriteRules.SPLIT_FDEPS:
            return try_split_fdep
        elif rule == RewriteRules.MERGE_BES:
            return try_merge_bes_in_or
        elif rule == RewriteRules.TRIM:
            # This method requires no element as input
            return trimming.trim
        elif rule == RewriteRules.REMOVE_DEPENDENCIES_TLE:
            return try_remove_dependencies
        elif rule == RewriteRules.REMOVE_DUPLICATES:
            return try_remove_duplicates
        elif rule == RewriteRules.FACTOR_COMMON_CAUSE:
            return try_factor_common_cause
        elif rule == RewriteRules.MERGE_IDENTICAL_GATES:
            # This method requires two gates as input
            return try_merge_identical_gates
        elif rule == RewriteRules.REMOVE_SINGLE_SUCCESSOR:
            return try_remove_gates_with_one_successor
        elif rule == RewriteRules.ADD_SINGLE_OR:
            return add_or_as_predecessor
        elif rule == RewriteRules.FLATTEN_GATE:
            return try_flatten_gate
        elif rule == RewriteRules.SUBSUME_GATE:
            return try_subsumption
        elif rule == RewriteRules.REPLACE_FDEP_BY_OR:
            return try_replace_fdep_by_or
        elif rule == RewriteRules.REMOVE_SUPERFLUOUS_FDEP:
            return try_remove_superfluous_fdep
        elif rule == RewriteRules.REMOVE_SUPERFLUOUS_FDEP_SUCCESSORS:
            return try_remove_fdep_successors
        else:
            raise DftInvalidArgumentException("Rewrite rule {} not known".format(rule))


def try_split_fdep(dft, fdep):
    """
    Split FDEPs with two or more children into single FDEPs with only one child.
    :param dft: DFT.
    :param fdep: FDEP.
    :return: True iff fdep was split.
    """
    # Check if rule can be applied
    if not isinstance(fdep, dft_gates.DftDependency):
        return False

    if len(fdep.children()) <= 2:
        return False

    if not numbers.is_one(fdep.probability):
        # Cannot be applied to PDEPs
        return False

    pos_add = 1
    trigger = fdep.trigger()
    dependents = fdep.children()[2:].copy()  # Keep first dependent event for original dependency
    for dependent in dependents:
        position = (fdep.position[0] - (50 * pos_add), fdep.position[1] - (75 * pos_add))
        new_fdep = dft_gates.DftDependency(dft.next_id(), "FDEP_{}_{}".format(fdep.name, pos_add), 1, [trigger, dependent], position)
        dft.add(new_fdep)
        fdep.remove_child(dependent)
        pos_add += 1
    return True


def try_merge_bes_in_or(dft, or_gate):
    """
    Try to merge BEs under an OR-gate into one BE.
    :param dft: DFT.
    :param or_gate: OR-gate.
    :return: True iff merge was successful.
    """
    # Check if rule is applicable
    if not isinstance(or_gate, dft_gates.DftOr):
        return False

    child_bes = []
    for child in or_gate.children():
        # Check if rule is applicable for BE
        if child.is_be() and len(child.parents()) <= 1 and not child.relevant and child.distribution == "exponential":
            # Repair rates need dedicated handling
            if numbers.is_zero(child.repair):
                child_bes.append(child)

    if len(child_bes) <= 1:
        return False

    # Merge BEs into one
    # Needs careful distinction between numbers represented as floats and rational functions represented as strings
    name = ""
    active_rate_float = 0
    passive_rate_float = 0
    active_rate_str = ""
    passive_rate_str = ""
    first_child = child_bes[0]
    for element in child_bes:
        # Set name
        if name:
            name += "_"
        name += element.name

        # Set active rate
        if isinstance(element.rate, float):
            active_rate_float += element.rate
        else:
            if active_rate_str:
                active_rate_str += " + "
            active_rate_str += "({})".format(element.rate)

        # Set passive rate
        if numbers.is_one(element.dorm):
            # Passive rate is active rate
            if isinstance(element.rate, float):
                passive_rate_float += element.rate
            else:
                if passive_rate_str:
                    passive_rate_str += " + "
                passive_rate_str += "({})".format(element.rate)
        elif numbers.is_zero(element.dorm):
            # Passive rate is zero
            pass
        else:
            if isinstance(element.dorm, float) and isinstance(element.rate, float):
                passive_rate_float += element.dorm * element.rate
            else:
                if passive_rate_str:
                    passive_rate_str += " + "
                passive_rate_str += "(({}) * ({}))".format(element.dorm, element.rate)

        assert numbers.is_zero(element.repair)
        # Remove merged element from DFT
        if element != first_child:
            dft.remove(element)

    # Update merged BE
    # Set name
    first_child.name = name

    # Set active rate
    if active_rate_str == "":
        first_child.rate = active_rate_float
    elif active_rate_float > 0:
        first_child.rate = "{} + ({})".format(active_rate_float, active_rate_str)
    else:
        first_child.rate = active_rate_str

    # Compute passive rate
    if passive_rate_str == "":
        passive_rate = passive_rate_float
    elif passive_rate_float > 0:
        passive_rate = "{} + ({})".format(passive_rate_float, passive_rate_str)
    else:
        passive_rate = passive_rate_str

    # Set dormancy factor
    if isinstance(first_child.rate, float) and isinstance(passive_rate, float):
        first_child.dorm = passive_rate / first_child.rate
    elif numbers.is_zero(passive_rate):
        first_child.dorm = 0
    elif first_child.rate == passive_rate:
        first_child.dorm = 1
    else:
        first_child.dorm = "({}) / ({})".format(passive_rate, first_child.rate)

    # Repair rate is zero
    first_child.repair = 0

    return True


def has_immediate_failure(dft, gate):
    """
    Checks whether a failure of the gate leads to an immediate failure of the top level element.
    In other words, all parents are OR-gates.
    :param dft: DFT.
    :param gate: Gate.
    :return: True iff failure leads to system failure.
    """
    if gate.element_id == dft.top_level_element.element_id:
        # Gate is top level element
        return True
    else:
        for parent in gate.parents():
            if isinstance(parent, dft_gates.DftOr):
                if has_immediate_failure(dft, parent):
                    return True
        return False


def try_remove_dependencies(dft, dependency):
    """
    Try to remove superfluous dependencies.
    These dependencies have a trigger which already leads to failure of the top level element.
    :param dft: DFT
    :param dependency: Dependency gate to remove.
    :return: True iff removal was successful.
    """
    # Check if rule is applicable
    if not isinstance(dependency, dft_gates.DftDependency):
        return False

    if not has_immediate_failure(dft, dependency.trigger()):
        return False

    # Remove superfluous dependency
    dft.remove(dependency)
    return True


def try_remove_duplicates(dft, gate):
    """
    Try to remove duplicate elements in gate successors.
    :param dft: DFT
    :param gate: Gate.
    :return: True iff removal was successful.
    """
    # Duplicates must be kept if order of children is important
    if not (isinstance(gate, dft_gates.DftAnd) or isinstance(gate, dft_gates.DftOr) or isinstance(gate, dft_gates.DftVotingGate)):
        return False

    # Check if duplicates exist
    duplicates = []
    for i in range(len(gate.children())):
        element = gate.children()[i]
        idi = element.element_id
        for j in range(i + 1, len(gate.children())):
            idj = gate.children()[j].element_id
            if idi == idj:
                duplicates.append(element)
    if not duplicates:
        return False

    # Remove duplicate
    for element in duplicates:
        gate.remove_child(element)

    return True


def try_factor_common_cause(dft, gate):
    """
    Try to factor out a common cause failure.
    A structure (A || B) && (B || C) with common cause B can be rewritten to B || (A && C).
    :param dft: DFT
    :param gate: Gate.
    :return: True iff common cause factoring was successful.
    """
    # Check if rule is applicable
    if not isinstance(gate, dft_gates.DftAnd):
        return False
    if len(gate.children()) <= 1:
        return False

    # Search for common cause candidates
    common_causes = None
    for or_gate in gate.children():
        if not isinstance(or_gate, dft_gates.DftOr):
            return False
        if len(or_gate.parents()) > 1:
            # Only AND-gate should be the parent
            return False

        children = set([c.element_id for c in or_gate.children()])
        if common_causes is None:
            common_causes = children
        else:
            # Intersection to only keep common cause failures
            common_causes &= children

    if len(common_causes) == 0:
        # No common cause failures found
        return False

    common_causes = [dft.get_element(c) for c in common_causes]

    # Remove common causes from OR-gates
    for or_gate in gate.children():
        for common_cause in common_causes:
            or_gate.remove_child(common_cause)

    # Create new AND-gate over remaining Or-gates
    # This gate represents the independent failures
    position = (gate.position[0] + 100, gate.position[1] + 150)
    independent_gate = dft_gates.DftAnd(dft.next_id(), gate.name + "_IndepFailures", gate.children(), position)
    dft.add(independent_gate)

    # Set element for common cause failures
    # If there are multiple ones, introduce a new gate
    if len(common_causes) > 1:
        position = (gate.position[0] - 100, gate.position[1] + 150)
        common_cause = dft_gates.DftOr(dft.next_id(), gate.name + "_CommonCauseFailures", common_causes, position)
        dft.add(common_cause)
    else:
        common_cause = common_causes[0]

    # Create new OR-gate as combination of common causes and independent failures
    position = (gate.position[0], gate.position[1] + 50)
    or_gate = dft_gates.DftOr(dft.next_id(), gate.name + "_2", [common_cause, independent_gate], position)
    # Add new gate as single child of existing gate
    # This will be simplified later on with rule REMOVE_SINGLE_SUCCESSOR
    dft.add(or_gate)
    while len(gate.children()) > 0:
        gate.remove_child(gate.children()[0])
    gate.add_child(or_gate)
    return True


def try_merge_identical_gates(dft, gate1, gate2):
    """
    (Rule #2): Try to merge gates with the same type and identical successors.
    These gates surely fail simultaneously and thus, one gate can be removed.
    :param dft: DFT
    :param gate1: First gate.
    :param gate2: Second gate (will be removed).
    :return: True iff merge and removal was successful.
    """
    # The same gate cannot be merged
    if gate1 == gate2:
        return False

    # Check if rule is applicable.
    if not gate1.compare(gate2, respect_ids=False):
        return False

    # Check if both gates are of type AND, OR, VOT, PAND, POR. As both gates have the same type it suffices to check gate1.
    if not (
        isinstance(gate1, dft_gates.DftAnd)
        or isinstance(gate1, dft_gates.DftOr)
        or isinstance(gate1, dft_gates.DftVotingGate)
        or isinstance(gate1, dft_gates.DftPriorityGate)
    ):
        return False

    if gate2.element_id == dft.top_level_element.element_id:
        return False

    if gate2.relevant:
        return False

    # Gates can be merged
    # Add parents of gate2 to gate1
    while gate2.parents():
        parent = gate2.parents()[-1]
        parent.replace_child(gate2, gate1)
        # Parent was removed from gate2 by replace_child

    # Merge names as well
    gate1.name += "_" + gate2.name
    # Remove gate2
    dft.remove(gate2)
    return True


def try_remove_gates_with_one_successor(dft, gate):
    """
    (Rule #3): Remove gates with just one successor.
    These gates will fail together with this child, so they can directly be eliminated.
    :param dft: DFT.
    :param gate: Gate to remove.
    :return: True iff gate has been removed.
    """
    # Check if rule is applicable.
    if not (
        isinstance(gate, dft_gates.DftOr)
        or isinstance(gate, dft_gates.DftAnd)
        or isinstance(gate, dft_gates.DftVotingGate)
        or isinstance(gate, dft_gates.DftPriorityGate)
    ):
        return False

    if gate.element_id == dft.top_level_element.element_id:
        return False

    if gate.relevant:
        return False

    if len(gate.children()) != 1:
        return False

    child = gate.children()[0]

    # Add child to parents
    while gate.parents():
        parent = gate.parents()[-1]
        # Replace gate by single child
        parent.replace_child(gate, child)
        # Parent was removed from gate by replace_child

    # Remove gate
    dft.remove(gate)
    return True


def try_flatten_gate(dft, gate):
    """
    (Rule #5): Flattening of AND-/OR-/PAND-gates.
    :param dft: DFT.
    :param gate: Gate to remove.
    :return: True iff gate has been removed.
    """
    # Check if rule is applicable.
    if not (isinstance(gate, dft_gates.DftOr) or isinstance(gate, dft_gates.DftAnd) or isinstance(gate, dft_gates.DftPand)):
        return False

    if gate.relevant:
        return False

    if len(gate.parents()) != 1:
        return False
    parent = gate.parents()[0]
    if gate.element_type != parent.element_type:
        return False

    if isinstance(parent, dft_gates.DftPand):
        if parent.inclusive != gate.inclusive:
            return False
        # Flattening for PAND only works if it is the left-most child
        if parent.children()[0] != gate:
            return False

        # Add children of PAND as first children of parent gate
        # First remove existing children and then later add them again
        existing_children = [child for child in parent.children()]
        for child in existing_children:
            parent.remove_child(child)
        assert not parent.children()
        for child in gate.children():
            parent.add_child(child)
        for child in existing_children:
            parent.add_child(child)
    else:
        # Add children of AND or OR to parent gate
        # The order is irrelevant here
        for child in gate.children():
            if child not in parent.children():
                parent.add_child(child)

    # Delete gate
    dft.remove(gate)
    return True


def try_subsumption(dft, gate):
    """
    (Rule #8, Rule #9): Subsumption of OR-gate by AND-gate or of AND-gate by OR-gate.
    :param dft: DFT.
    :param gate: Gate which could be subsumed.
    :return: True iff subsumption was possible.
    """
    # Check if rule is applicable.
    if not (isinstance(gate, dft_gates.DftOr) or isinstance(gate, dft_gates.DftAnd)):
        return False

    if gate.relevant:
        return False

    if len(gate.parents()) != 1:
        return False
    parent = gate.parents()[0]
    # Check that parent is of "opposite" type
    if isinstance(gate, dft_gates.DftOr):
        if not isinstance(parent, dft_gates.DftAnd):
            return False
    else:
        assert isinstance(gate, dft_gates.DftAnd)
        if not isinstance(parent, dft_gates.DftOr):
            return False

    # Check if a child occurs in both gate and parent
    for child in gate.children():
        if child in parent.children():
            # Can remove gate
            dft.remove(gate)
            return True

    return False


def add_or_as_predecessor(dft, element, name=None):
    """
    (Rule #4): Add an OR-gate as the single predecessor of element.
    This is helpful for other rules, e.g., rule #24.
    :param dft: DFT.
    :param element: Element which gets an OR as predecessor.
    :param name: Name of new OR-gate.
    :return: The new OR-gate or None.
    """
    if name is None:
        name = "OR_{}".format(dft.next_id())
    # Create empty OR-gate
    position = (element.position[0] - 100, element.position[1] - 150)
    or_gate = dft_gates.DftOr(dft.next_id(), name, [], position)

    # Replace current element by or_gate in all parents
    while element.parents():
        parent = element.parents()[-1]
        parent.replace_child(element, or_gate)
        # Parent was removed from element by replace_child

    # Add element to OR-gate
    or_gate.add_child(element)
    dft.add(or_gate)
    return or_gate


def check_dynamic_predecessor(dft, element):
    """
    Check whether element has at least one dynamic element (except a dependency) in its predecessor closure.
    Performs DFS of predecessors.
    :param dft: DFT.
    :param element: Element.
    :return: True iff the predecessor closure of element contains at least one dynamic element.
    """
    if element.is_dynamic() and not isinstance(element, dft_gates.DftDependency):
        return True
    if element.element_id == dft.top_level_element.element_id:
        return False
    for elem in element.parents():
        if check_dynamic_predecessor(dft, elem):
            return True
    return False


def check_for_cycle(dft, element, current):
    """
    Check for cycle by checking whether element contains itself in its predecessor closure.
    The cycle check excludes dependencies and restrictors.
    :param dft: DFT.
    :param element: Element to search for.
    :param current: Current element.
    :return: True iff the predecessor closure of current contains element.
    """
    if current.element_id == element.element_id:
        return True
    if (
        current.is_dynamic()
        and not isinstance(current, dft_gates.DftDependency)
        and not isinstance(current, dft_gates.DftSeq)
        and not isinstance(current, dft_gates.DftMutex)
    ):
        return False
    if current.element_id == dft.top_level_element.element_id:
        return False
    for parent in current.parents():
        if check_for_cycle(dft, element, parent):
            return True
    return False


def try_replace_fdep_by_or(dft, fdep):
    """
    (Rule #24): Eliminate FDEPs by introducing an OR-gate.
    Let A be the trigger and B be the dependent element.
    Both must be connected to the top level element.
    B must have only one predecessor and no SPARE or PAND/POR in its  predecessor closure.
    :param dft: DFT.
    :param fdep: FDEP which can possibly be removed.
    :return: True iff fdep has been removed.
    """
    if not isinstance(fdep, dft_gates.DftDependency):
        return False
    if fdep.probability != 1:
        return False
    # Check if fdep has more than one dependent element
    if len(fdep.children()) > 2:
        return False
    trigger = fdep.trigger()
    dependent = fdep.dependent()[0]

    # Check if both trigger and dependent are part of the top module
    top_module = dft.get_module(dft.top_level_element)
    if trigger.element_id not in top_module or dependent.element_id not in top_module:
        return False
    # Check if dependent has some dynamic elements in the predecessor closure
    if check_dynamic_predecessor(dft, dependent):
        return False
    # Check if rewriting would yield a cycle
    for parent in dependent.parents():
        if check_for_cycle(dft, trigger, parent):
            return False

    # Add OR in front of dependent
    or_gate = add_or_as_predecessor(dft, dependent, name="OR_" + dependent.name)
    if not or_gate:
        return False
    dft.remove(fdep)
    or_gate.add_child(trigger)
    return True


def try_remove_superfluous_fdep(dft, fdep):
    """
    (Rule #25, Rule #26): Eliminate superfluous FDEP from AND or OR.
    This FDEP is triggered after the failure of the dependent element and thus, it does not influence anything else.
    :param dft: DFT.
    :param fdep: FDEP to check.
    :return: True iff elimination was successful.
    """
    # Check if rule can be applied
    if not isinstance(fdep, dft_gates.DftDependency):
        return False

    # Check if fdep has more than one dependent element
    if len(fdep.children()) > 2:
        return False
    trigger = fdep.trigger()
    dependent = fdep.dependent()[0]

    # Trigger is single parent of dependent (apart from fdep)
    if len(dependent.parents()) > 2:
        return False
    if trigger not in dependent.parents():
        return False

    if isinstance(trigger, dft_gates.DftAnd):
        # FDEP is superfluous (Rule #25)
        dft.remove(fdep)
        return True

    if isinstance(trigger, dft_gates.DftOr):
        # FDEP is possibly superfluous (Rule #26)
        # Check for FDEPs from other children of the parent
        for child in trigger.children():
            if child != dependent:
                # Check that other child has FDEP to dependent as well
                has_fdep = False
                for parent in child.parents():
                    if isinstance(parent, dft_gates.DftDependency):
                        if len(parent.children()) == 2 and parent.children()[0] == child and parent.children()[1] == dependent:
                            has_fdep = True
                            break
                if not has_fdep:
                    # Other children have no valid FDEP to dependent
                    return False
        # FDEP is superfluous
        dft.remove(fdep)
        return True

    return False


def try_remove_fdep_successors(dft, fdep):
    """
    (Rule #27, Rule #28): Eliminate FDEP between two successors of an OR or PAND.
    Only supports FDEPs with one common predecessor.
    :param dft: DFT.
    :param fdep: FDEP to check.
    :return: True iff elimination was successful.
    """
    # Check if rule can be applied
    if not isinstance(fdep, dft_gates.DftDependency):
        return False

    # Check if fdep has more than one dependent element
    if len(fdep.children()) > 2:
        return False
    trigger = fdep.trigger()
    dependent = fdep.dependent()[0]

    # Dependent has single parent (apart from fdep)
    if len(dependent.parents()) > 2:
        return False
    parent = dependent.parents()[0] if not isinstance(dependent, dft_gates.DftDependency) else dependent.parents()[1]

    # Trigger has the same parent
    if trigger not in parent.children():
        return False

    if isinstance(parent, dft_gates.DftOr):
        # FDEP is superfluous (Rule #27)
        dft.remove(fdep)
        return True

    if isinstance(parent, dft_gates.DftPand):
        # FDEP is possibly superfluous (Rule #28)
        # Check if dependent is left of trigger
        dependent_is_left = False
        for child in parent.children():
            if child == trigger:
                dependent_is_left = False
                break
            elif child == dependent:
                dependent_is_left = True
                break
        if dependent_is_left:
            # FDEP is superfluous
            dft.remove(fdep)
            return True

    return False
