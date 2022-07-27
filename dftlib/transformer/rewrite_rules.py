import dftlib.storage.dft_gates as dft_gates

"""
Rewrite rules for DFT simplification.
The rules are in parts based on:
Junges, S., Guck, D., Katoen, J.-P., Rensink, A., Stoelinga, M., 2017.
'Fault trees on a diet: automated reduction by graph rewriting'. Form Asp Comp 29, 651–703.
https://doi.org/10.1007/s00165-016-0412-0
"""


def split_fdeps(dft):
    """
    Split FDEPs with two or more children into single FDEPs with only one child.
    :param dft: DFT.
    :return: True if at least one FDEP is split.
    """
    split = False
    # Remember FDEPs as the elements will later change through removal/adding
    fdeps = [fdep for _, fdep in dft.elements.items() if isinstance(fdep, dft_gates.DftDependency)]
    for fdep in fdeps:
        pos_add = 1
        trigger = fdep.outgoing[0]
        for dependent in fdep.outgoing[2:]:  # Keep first dependent event for original dependency
            position = (fdep.position[0] - (50 * pos_add), fdep.position[1] - (75 * pos_add))
            new_fdep = dft_gates.DftDependency(dft.next_id(), 'FDEP_{}'.format(dft.next_id()), 1, [trigger, dependent], position)
            dft.add(new_fdep)
            fdep.remove_child(dependent)
            pos_add += 1
            split = True
    return split


def try_merge_bes_in_or(dft, or_gate):
    """
    Try to merge BEs under an OR-gate into one BE.
    :param dft: DFT.
    :param or_gate: OR gate.
    :return: True iff merge was successful.
    """
    # Check if rule is applicable
    if not isinstance(or_gate, dft_gates.DftOr):
        return False

    child_bes = []
    for child in or_gate.outgoing:
        # Check if rule is applicable for BE
        if child.is_be() and len(child.ingoing) <= 1 and not child.relevant and child.distribution == "exponential":
            child_bes.append(child)

    if len(child_bes) <= 1:
        return False

    # Merge BEs into one
    first_child = child_bes[0]
    passive_rate = first_child.dorm * first_child.rate
    for element in child_bes[1:]:
        first_child.name += "_" + element.name
        # Update rates
        first_child.rate += element.rate
        passive_rate += element.dorm * element.rate
        dft.remove(element)

    first_child.dorm = passive_rate / first_child.rate
    return True


def try_merge_or(dft, or_gate):
    """
    Try to merge two OR gates in different levels.
    :param dft: DFT
    :param or_gate: OR gate to remove.
    :return: True iff merge was successful.
    """
    # Check if rule is applicable
    if not isinstance(or_gate, dft_gates.DftOr):
        return False

    if len(or_gate.ingoing) != 1:
        return False

    if or_gate.relevant:
        return False

    parent = or_gate.ingoing[0]
    if not isinstance(parent, dft_gates.DftOr):
        return False

    # Add children to parent gate
    for child in or_gate.outgoing:
        if child not in parent.outgoing:
            parent.add_child(child)

    # Delete OR-gate
    dft.remove(or_gate)
    return True


def has_immediate_failure(dft, gate):
    """
    Checks whether a failure of the gate leads to an immediate failure of the top level element.
    In other words, all parents are OR gates.
    :param dft: DFT.
    :param gate: Gate.
    :return: True iff failure leads to system failure.
    """
    if gate.element_id == dft.top_level_element.element_id:
        # Gate is top level element
        return True
    else:
        for parent in gate.ingoing:
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

    trigger = dependency.outgoing[0]
    if not has_immediate_failure(dft, trigger):
        return False

    # Remove superfluous dependency
    dft.remove(dependency)
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
    if not (isinstance(gate1, dft_gates.DftAnd) or isinstance(gate1, dft_gates.DftOr) or isinstance(gate1, dft_gates.DftVotingGate) or isinstance(gate1,
                                                                                                                                                  dft_gates.DftPriorityGate)):
        return False

    # Gates can be merged
    # Add parents of gate2 to gate1
    for parent in gate2.ingoing:
        if gate1 not in parent.outgoing:
            parent.add_child(gate1)
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
    :return: True if gate has been removed.
    """
    # Check if rule is applicable.
    if not (isinstance(gate, dft_gates.DftOr) or isinstance(gate, dft_gates.DftAnd) or isinstance(gate, dft_gates.DftVotingGate) or isinstance(gate, dft_gates.DftPriorityGate)):
        return False
    if gate.element_id == dft.top_level_element.element_id:
        return False
    if gate.relevant:
        return False

    if len(gate.outgoing) != 1:
        return False

    child = gate.outgoing[0]

    # Add child to parents
    for parent in gate.ingoing:
        if child not in parent.outgoing:
            parent.add_child(child)
    # Remove gate
    dft.remove(gate)
    return True


def add_or_as_predecessor(dft, element, name=None):
    """
    (Rule #4): Add an OR-gate as the single predecessor of element.
    This is helpful for other rules, e.g., rule #24.
    :param dft: DFT.
    :param element: Element which gets an OR as predecessor.
    :param name: Name of new OR-gate.
    :return: The new OR gate or None.
    """
    if name is None:
        name = "OR_{}".format(dft.next_id())
    # Remember all parents
    parents = [parent for parent in element.ingoing]
    # Remove element from all parents
    for parent in parents:
        parent.remove_child(element)
    position = (element.position[0] - 100, element.position[1] - 150)
    or_gate = dft_gates.DftOr(dft.next_id(), name, [element], position)
    dft.add(or_gate)
    for parent in parents:
        parent.add_child(or_gate)
    return or_gate


def check_dynamic_predecessor(dft, element):
    """
    Check whether element has at least one dynamic element (except a dependency) in its predecessor closure.
    :param dft: DFT.
    :param element: Element.
    :return: True iff the predecessor closure of element contains at least one dynamic element.
    """
    if element.is_dynamic() and not isinstance(element, dft_gates.DftDependency):
        return True
    if element.element_id == dft.top_level_element.element_id:
        return False
    for elem in element.ingoing:
        if check_dynamic_predecessor(dft, elem):
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
    if len(fdep.outgoing) > 2:
        return False
    trigger = fdep.outgoing[0]
    dependent = fdep.outgoing[1]

    # Check if both trigger and dependent are part of the top module
    top_module = dft.get_module(dft.top_level_element)
    if trigger.element_id not in top_module or dependent.element_id not in top_module:
        return False
    # Check if dependent has some dynamic elements in the predecessor closure
    if check_dynamic_predecessor(dft, dependent):
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
    if len(fdep.outgoing) > 2:
        return False
    trigger = fdep.outgoing[0]
    dependent = fdep.outgoing[1]

    # Trigger is single parent of dependent (apart from fdep)
    if len(dependent.ingoing) > 2:
        return False
    if trigger not in dependent.ingoing:
        return False

    if isinstance(trigger, dft_gates.DftAnd):
        # FDEP is superfluous (Rule #25)
        dft.remove(fdep)
        return True

    if isinstance(trigger, dft_gates.DftOr):
        # FDEP is possibly superfluous (Rule #26)
        # Check for FDEPs from other children of the parent
        for child in trigger.outgoing:
            if child != dependent:
                # Check that other child has FDEP to dependent as well
                has_fdep = False
                for parent in child.ingoing:
                    if isinstance(parent, dft_gates.DftDependency):
                        if len(parent.outgoing) == 2 and parent.outgoing[0] == child and parent.outgoing[1] == dependent:
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
    if len(fdep.outgoing) > 2:
        return False
    trigger = fdep.outgoing[0]
    dependent = fdep.outgoing[1]

    # Dependent has single parent (apart from fdep)
    if len(dependent.ingoing) > 2:
        return False
    parent = dependent.ingoing[0] if not isinstance(dependent, dft_gates.DftDependency) else dependent.ingoing[1]

    # Trigger has the same parent
    if trigger not in parent.outgoing:
        return False

    if isinstance(parent, dft_gates.DftOr):
        # FDEP is superfluous (Rule #27)
        dft.remove(fdep)
        return True

    if isinstance(parent, dft_gates.DftPand):
        # FDEP is possibly superfluous (Rule #28)
        # Check if dependent is left of trigger
        dependent_is_left = False
        for child in parent.outgoing:
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
