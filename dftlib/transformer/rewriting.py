import dftlib.transformer.transformation


class Message:
    """docstring for Message"""

    def __init__(self, level, text):
        self.level = level
        self.text = text

    def toString(self):
        string = str(self.level) + ': ' + str(self.text)
        return string

    def get_level(self):
        return self.level

    def get_text(self):
        return self.text


class Logger:
    messages = list()

    def add_message(self, message):
        self.messages.append(message)

    def pop_message(self):
        return self.messages.pop(len(self.messages))

    def clear(self):
        self.messages.clear()

    def get_messages(self):
        if self.messages:
            string = ''
            for msg in self.messages:
                if string:
                    # Insert '#' for separating 
                    string = string + '#' + msg.toString()
                else:
                    string = msg.toString()
            return string
        else:
            return ''


# Global Logger
simpLogger = Logger()

# Global Transformer
transformer = dftlib.transformer.transformation.Transformation()


# """"""""""""""""""""""""""""""""""""""""""#
#       Methods for DFT-Simplifying        #
# """"""""""""""""""""""""""""""""""""""""""#


def split_fdeps(dft):
    """
    Split fdeps with two or more children into single fdeps with only one child.
    :param dft: DFT.
    :param fdep: FDEP to check and eventually to split.
    :return: True if fdep is split.
    """
    # Check all fdeps and save the interesting ones
    fdeps = []
    for (_, fdep) in dft.elements.items():
        if fdep.element_type == 'fdep':
            if len(fdep.dependent) > 1:
                fdeps.append(fdep)

    # Only go on if fdeps is not empty
    if fdeps:
        for fdep in fdeps:
            pos_add = 1
            trigger = fdep.trigger
            dependent = fdep.dependent
            num_dep = len(dependent)
            while num_dep > 1:
                # Create new FDEP with last dependent element
                position = (fdep.position[0] - (50 * pos_add), fdep.position[1] - (75 * pos_add))
                new_fdep = dft.new_gate('FDEP_' + str(dft.max_id + 1), 'fdep', [], position)
                # Add gate to transformer
                transformer.addFdepAdd()
                pos_add += 1
                # Add parents and children
                new_fdep.add_child(trigger)
                rem_dep = dependent.pop()
                new_fdep.add_child(rem_dep)
                num_dep -= 1
                fdep.remove_child(rem_dep)


def try_merge_bes_in_or(dft, or_gate):
    """
    Try to merge BEs under an OR into one BE.
    :param dft: DFT.
    :param or_gate: OR gate.
    :return: True iff merge was successful.
    """
    # Check if rule is applicable
    if or_gate.element_type != 'or':
        return False

    child_bes = []
    for child in or_gate.outgoing:
        if child.is_be() and len(child.ingoing) <= 1 and child.dorm == 1 and not child.relevant:
            child_bes.append(child)

    if len(child_bes) <= 1:
        return False

    # Merge BEs into one
    first_child = child_bes[0]
    for element in child_bes[1:]:
        first_child.name += "_{}".format(element.name)
        first_child.rate += element.rate
        # TODO: combine dormancy factors as well
        dft.remove(element)
        # Add removed element to transformer
        transformer.addBe()

    return True


def try_merge_or(dft, or_gate):
    """
    Try to merge two OR gates in different levels.
    :param dft: DFT
    :param or_gate: OR gate to remove.
    :return: True iff merge was successful.
    """
    # Check if rule is applicable
    if or_gate.element_type != 'or':
        return False

    if len(or_gate.ingoing) != 1:
        return False

    if or_gate.relevant:
        return False

    parent = or_gate.ingoing[0]
    if parent.element_type != 'or':
        return False

    # Add children to parent gate
    for child in or_gate.outgoing:
        if child not in parent.outgoing:
            parent.add_child(child)

    # Delete or gate and add to transformer
    dft.remove(or_gate)
    transformer.addOrRem()

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
        return gate.element_type == 'or'
    else:
        for parent in gate.ingoing:
            if parent.element_type == 'or':
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
    if dependency.element_type != 'fdep':
        return False

    trigger = dependency.trigger
    if not has_immediate_failure(dft, trigger):
        return False

    # Remove superfluous dependency and add to transformer
    dft.remove(dependency)
    transformer.addFdepRem()

    return True


def try_merge_identical_gates(dft, gate):
    """
    (Rule #2): Try to merge gates with the same type and identical successors.
    These gates surely fail simultaneously thus one gate can be removed.
    :param dft: DFT
    :param gate: Gate to merge.
    :return: True iff merge and removal was successful.
    """
    # Check if rule is applicable. Therefore, check if gate is no SPARE or FDEP
    if gate.element_type == 'fdep' or gate.element_type == 'spare' or gate.element_type == 'be':
        return False

    # Check if gate has more than one parent (for simplicity atm)
    if len(gate.ingoing) != 1:
        return False
    parent = gate.ingoing[0]

    # Check if parent has more than this gate as child
    if len(parent.outgoing) == 1:
        return False

    potChild = []
    for child in parent.outgoing:
        if child.element_type == gate.element_type and child.element_id != gate.element_id:
            if len(child.ingoing) == 1:
                if gate.compare_successors(child):
                    potChild.append(child)

    # Check if potChild is empty
    if not potChild:
        return False
    else:
        for child in potChild:
            dft.remove(child)

            # Add removed child to transformer
            if child.element_type == 'and':
                transformer.addAnd()
            elif child.element_type == 'or':
                transformer.addOrRem()
            elif child.element_type == 'vot':
                transformer.addVot()
            elif child.element_type == 'pand':
                transformer.addPand()
            elif child.element_type == 'por':
                transformer.addPor()

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
    if gate.element_type == 'fdep' or gate.element_type == 'spare' or gate.element_type == 'be' or gate.element_id == dft.top_level_element.element_id:
        return False

    if gate.relevant:
        return False

    if len(gate.outgoing) != 1:
        return False

    child = gate.outgoing[0]

    # Add child to parents
    parents = []
    for parent in gate.ingoing:
        parents.append(parent)
        if child not in parent.outgoing:
            parent.add_child(child)

    dft.remove(gate)

    for parent in parents:
        assert gate not in parent.outgoing

    # Add removed child to transformer
    if gate.element_type == 'and':
        transformer.addAnd()
    elif gate.element_type == 'or':
        transformer.addOrRem()
    elif gate.element_type == 'vot':
        transformer.addVot()
    elif gate.element_type == 'pand':
        transformer.addPand()
    elif gate.element_type == 'por':
        transformer.addPor()

    return True


def add_or_in_between(dft, element):
    """
    (Rule #4): Replace the single successor of an element by an OR.
    This is helpful for other rules, e.g., rule #24.
    :param dft: DFT.
    :param element: Element which gets an OR as predecessor.
    :return: The new OR gate or None.
    """
    # Check if predecessor is already an OR
    for elem in element.ingoing:
        if elem.element_type == 'or':
            return None

    for elem in element.ingoing:
        if not elem.element_type == 'fdep':
            parent = elem

    # Remove element from parents children
    parent.remove_child(element)
    position = (element.position[0] - 100, element.position[1] - 150)
    or_gate = dft.new_gate('OR_' + str(dft.max_id + 1), 'or', [], position)

    # Add OR to transformer
    transformer.addOrAdd()

    parent.add_child(or_gate)
    or_gate.add_child(element)

    return or_gate


def is_connected(a, b):
    """
    Check if element b is reachable from a.
    :param a: First element a.
    :param b: Second element b.
    :return: True if b is reachable from a. False otherwise.
    """
    for elem in a.outgoing:
        if elem.compare(b):
            return True
        if is_connected(elem, b):
            return True

    return False


def try_elim_fdeps_with_new_or(dft, fdep):
    """
    (Rule #24): Eliminate FDEPs by introduction of an OR.
    Let A be the trigger and B be the dependent element. Both have to be TopConnected. B must have only one predecessor and no SPARE or PAND/POR in its 
    predecessor closure.
    :param dft: DFT.
    :param fdep: FDEP which can eventually be removed.
    :return: True if fdep has been removed.
    """
    # Check if fdep has more than one dependent element
    if len(fdep.outgoing) > 2:
        return False

    # Check if trigger and dependent element top connected is.
    if fdep.element_type != 'fdep':
        return False
    else:
        trigger = fdep.trigger
        dependent = fdep.dependent[0]
        if not is_connected(dft.top_level_element, trigger) or not is_connected(dft.top_level_element, dependent):
            return False

    # Check if B has some dynamic elements in the predecessor closure
    for dyn in dft.get_dynamics():
        if dependent in dyn.outgoing:
            return False

    # Check if B has only one predecessor
    if (len(dependent.ingoing) - 1) != 1:
        return False

    # Check if predecessor of B is OR
    if dependent.ingoing[0].element_type == 'or':
        # Remove fdep and add trigger to OR and add removed FDEP to transformer
        dft.remove(fdep)
        transformer.addFdepRem()
        dependent.ingoing[0].add_child(trigger)
    else:
        # Add OR in front of B
        or_gate = add_or_in_between(dft, dependent)
        if not or_gate is None:
            or_gate.add_child(trigger)
            dft.remove(fdep)
            transformer.addFdepRem()
        else:
            return False

    return True


def try_rem_superfluous_fdeps(dft, fdep):
    """
    (Rule #25): Eliminate superfluous FDEP from AND/PAND/OR/POR/VOT.
    This FDEP is triggered after the failure of the dependent element and thus it does not influence anything else.
    :param dft: DFT.
    :param fdep: FDEP to check.
    :return: True iff elimination was successful.
    """
    # Check if fdep is suitable
    if fdep.element_type != 'fdep':
        return False

    if len(fdep.dependent) > 1:
        return False

    trigger = fdep.trigger
    dependent = fdep.dependent[0]

    if not dependent in trigger.outgoing:
        return False

    # Remove superfluous fdep and add to transformer
    dft.remove(fdep)
    transformer.addFdepRem()

    return True


def try_rem_fdep_succ_or(dft, fdep):
    """
    (Rule #27): Eliminate FDEP between two successors of an OR.
    This FDEP is superfluous. Only supports FDEPs with one common predecessor.
    :param dft: DFT.
    :param fdep: FDEP to check.
    :return: True iff elimination was successful.
    """
    # Check if fdep is suitable
    if fdep.element_type != 'fdep':
        return False

    if len(fdep.dependent) > 1:
        return False

    trigger = fdep.trigger
    dependent = fdep.dependent[0]

    # Check if trigger and dependent have the same parent 
    if len_without_deps(dependent.ingoing) != 1:
        return False

    parent = dependent.ingoing[0]
    if parent.element_type != 'or':
        return False

    if not trigger in parent.outgoing:
        return False

    # Trigger and dependent element are both successors of the same or, thus remove the fdep and add it to transformer
    dft.remove(fdep)
    transformer.addFdepRem()

    return True


def try_rem_fded_succ_pand(dft, fdep):
    """
    (Rule #28): Eliminate FDEP between two successors of an PAND.
    If the trigger element is right to the dependent element, the FDEP is superfluous.
    :param dft: DFT.
    :param pand: FDEP to check.
    :return: True iff elimination was successful.
    """
    # Check if fdep is suitable
    if fdep.element_type != 'fdep':
        return False

    if len(fdep.dependent) > 1:
        return False

    trigger = fdep.trigger
    dependent = fdep.dependent[0]

    # Check if trigger and dependent have the same parent
    if len_without_deps(dependent.ingoing) != 1:
        return False

    parent = dependent.ingoing[0]
    if parent.element_type != "pand":
        return False

    if not trigger in parent.outgoing:
        return False

    # Check if the dependent element is left to the trigger
    first = False
    for child in parent.outgoing:
        if not first:
            if child.compare(dependent):
                first = True
            else:
                # Trigger is first
                break

    if not first:
        return False
    else:
        # Remove FDEP and add to transformer
        dft.remove(fdep)
        transformer.addFdepRem()
        return True


def len_without_deps(element):
    """
    Calculate len without FDEPs.
    :param element: The elements of interest.
    :return: length without FDEPs.
    """
    if not len(element):
        return False

    count = 0
    for elem in element:
        if elem.element_type == 'fdep':
            count += 1

    result = len(element) - count
    assert result > -1

    return result


def simplify_dft(dft, rules=["1", "2", "3", "4", "5", "6", "7"]):
    """
    Simplify DFT.
    :param dft: DFT.
    :return: Simplified DFT.
    """

    if rules:
        changed = True
        while changed:
            for _, element in dft.elements.items():

                if '1' in rules:
                    changed = try_merge_or(dft, element)
                    if changed:
                        break
                if '2' in rules:
                    changed = try_merge_bes_in_or(dft, element)
                    if changed:
                        break
                if '3' in rules:
                    changed = try_remove_dependencies(dft, element)
                    if changed:
                        break
                if '4' in rules:
                    changed = try_merge_identical_gates(dft, element)
                    if changed:
                        break
                if '5' in rules:
                    changed = try_remove_gates_with_one_successor(dft, element)
                    if changed:
                        break
                if '6' in rules:
                    changed = try_elim_fdeps_with_new_or(dft, element)
                    if changed:
                        break
                if '7' in rules:
                    changed = try_rem_superfluous_fdeps(dft, element)
                    if changed:
                        break
                if '7' in rules:
                    changed = try_rem_fdep_succ_or(dft, element)
                    if changed:
                        break
                if '7' in rules:
                    changed = try_rem_fded_succ_pand(dft, element)
                    if changed:
                        break

    # Prepare output from transformer
    prepareTransformer(dft)

    return dft


def prepareTransformer(dft):
    transformer.setNumberOfElements(dft.size_elements())
    staticNum = transformer.sumStatic()
    dynamicNum = transformer.sumDynamic()
    beNum = transformer.sumBEs()

    if beNum == 1:
        beString = 'BE'
    else:
        beString = 'BEs'

    if staticNum == 1:
        staticString = 'Static Gate'
    else:
        staticString = 'Static Gates'

    if dynamicNum == 1:
        dynamicString = 'Dynamic Gate'
    else:
        dynamicString = 'Dynamic Gates'

    # Add message to logger
    simpLogger.add_message(
        Message('Info', 'Removed {} {}, {} {} and {} {} from DFT while simplifying.'.format(beNum, beString, staticNum, staticString, dynamicNum, dynamicString)))

    # If FDEPs were splitted, tell here
    addedFdeps = transformer.getFdepsAdd()
    if addedFdeps > 0:
        if addedFdeps == 1:
            simpLogger.add_message(Message('Info', 'Added 1 FDEP while splitting FDEPs.'))
        else:
            simpLogger.add_message(Message('Info', 'Added {} FDEPs while splitting FDEPs.'.format(transformer.getFdepsAdd())))

    # If ORs were added, tell here
    addedOrs = transformer.getOrsAdd()
    if addedOrs > 0:
        if addedOrs == 1:
            simpLogger.add_message(Message('Info', 'Added 1 OR Gate while simplifying.'))
        else:
            simpLogger.add_message(Message('Info', 'Added {} OR Gates while simplifying.'.format(transformer.getOrsAdd())))

    # Check for percentage of optimisation
    simpLogger.add_message(Message('Debug', 'Alt: {} Neu: {}'.format(transformer.getNumberOfElements(), dft.size_elements())))
    count = transformer.getNumberOfElements() - dft.size_elements()
    if count == 1:
        simpLogger.add_message(Message('Info', 'Optimisation removes 1 Element (-{}%).'.format(transformer.getPercentage(dft.size_elements()))))
    elif count == -1:
        simpLogger.add_message(Message('Info', 'Optimisation adds 1 Element (+{}%).'.format(transformer.getPercentage(dft.size_elements()))))
    elif count < -1:
        simpLogger.add_message(Message('Info', 'Optimisation adds {} Elements (+{}%).'.format(count * -1, transformer.getPercentage(dft.size_elements()))))
    else:
        simpLogger.add_message(Message('Info', 'Optimisation removes {} Elements (-{}%).'.format(count, transformer.getPercentage(dft.size_elements()))))
