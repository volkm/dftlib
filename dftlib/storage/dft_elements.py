from dftlib.exceptions.exceptions import DftTypeNotKnownException


def create_from_json(json):
    """
    Create DFT element from JSON string.
    :param json: JSON string.
    :return: DFT element.
    """
    assert json['group'] == "nodes"
    # Parse data from json
    data = json['data']
    element_id = int(data['id'])
    name = data['name']
    element_type = data['type']
    if 'position' in json:
        position = (json['position']['x'], json['position']['y'])
    else:
        position = (0, 0)

    if element_type == "be" or element_type == "be_exp":
        # BE
        rate = float(data['rate'])
        dorm = float(data['dorm'])
        if 'repair' in data:
            repair = float(data['repair'])
        else:
            repair = 0
        element = DftBe(element_id, name, rate, dorm, repair, position)
    elif element_type == "and":
        # AND
        element = DftAnd(element_id, name, [], position)
    elif element_type == "or":
        # OR
        element = DftOr(element_id, name, [], position)
    elif element_type == "vot":
        # VOTing gate
        threshold = int(data['voting'])
        element = DftVotingGate(element_id, name, threshold, [], position)
    elif element_type == "fdep":
        # Functional dependency (FDEP)
        element = DftDependency(element_id, name, 1, [], position)
    elif element_type == "pdep":
        # PDEP (dependency with probability)
        assert 'probability' in data
        prob = float(data['probability'])
        element = DftDependency(element_id, name, prob, [], position)
    elif element_type == "pand":
        # PAND
        element = DftPand(element_id, name, [], position)
    elif element_type == "por":
        # POR
        element = DftPor(element_id, name, [], position)
    elif element_type == "spare":
        # SPARE
        element = DftSpare(element_id, name, [], position)
    elif element_type == "seq":
        # Sequence enforcer
        element = DftSeq(element_id, name, [], position)
    elif element_type == "mutex":
        # Mutex
        element = DftMutex(element_id, name, [], position)
    else:
        raise DftTypeNotKnownException("Type '{}' not known.".format(element_type))

    if 'relevant' in data:
        element.relevant = data['relevant']
    return element


class DftElement:
    """
    Class containing a DFT element.
    """

    def __init__(self, element_id, name, element_type, position):
        self.element_id = element_id
        self.name = name
        self.element_type = element_type
        self.position = position
        self.ingoing = []
        self.outgoing = []
        self.isDynamic = False
        self.relevant = False

    def is_dynamic(self):
        """
        Get whether the element is dynamic.
        :return: True iff element is dynamic.
        """
        return self.isDynamic

    def is_be(self):
        """
        Get whether the element is a BE.
        :return: True iff element is a BE.
        """
        return self.element_type == "be"

    def is_gate(self):
        """
        Get whether the element is a gate.
        :return: True iff element is a gate.
        """
        return not self.is_be()

    def remove_parent(self, element):
        """
        Remove parent.
        :param element: Parent to remove.
        """
        assert element in self.ingoing
        self.ingoing.remove(element)

    def set_relevant(self, relevant=True):
        """
        Set whether the element is relevant (and will not be set to 'Don't Care' for example).
        :param relevant: Whether the element is relevant.
        """
        self.relevant = relevant

    def get_json(self):
        """
        Get JSON string.
        :return: JSON string.
        """
        data = dict()
        data['id'] = str(self.element_id)
        data['name'] = str(self.name)
        data['type'] = self.element_type
        if self.relevant:
            data['relevant'] = True
        position = dict()
        position["x"] = self.position[0]
        position["y"] = self.position[1]
        json = {
            "data": data,
            "position": position,
            "group": "nodes"
        }
        return json

    def __str__(self):
        return "{} - '{}' ({})".format(self.element_type, self.name, self.element_id)

    def compare(self, other):
        """
        Compare elements.
        :param other: Other element.
        :return: True iff both elements are equal.
        """
        if self.element_id != other.element_id:
            # raise Exception("Ids are not equal: {} and {}".format(self.element_id, other.element_id))
            return False
        if self.element_type != other.element_type:
            # raise Exception(
            #    "Element types are not equal for {}: {} and {}".format(self, self.element_type, other.element_type))
            return False
        list_outgoing = [elem.element_id for elem in other.outgoing]
        for element in self.outgoing:
            if element.element_id in list_outgoing:
                list_outgoing.remove(element.element_id)
            else:
                # raise Exception("Element {} is not contained in other for {}.".format(element, self))
                return False
        if len(list_outgoing) > 0:
            # raise Exception("Some elements are not contained in {}.".format(self))
            return False

        return True


class DftBe(DftElement):
    """
    Basic element (BE).
    """

    def __init__(self, element_id, name, rate, dorm, repair, position):
        DftElement.__init__(self, element_id, name, "be", position)
        assert self.is_be()
        self.rate = rate
        self.dorm = dorm
        self.repair = repair

    def get_json(self):
        json = DftElement.get_json(self)
        json['data']['rate'] = str(self.rate)
        json['data']['dorm'] = str(self.dorm)
        json['data']['repair'] = str(self.repair)
        return json

    def __str__(self):
        s = super().__str__()
        s += " with rate {}".format(self.rate)
        if self.dorm != 1 and self.repair > 0:
            s += " and repair {} ({})".format(self.repair, self.dorm)
        elif self.dorm != 1:
            s += " ({})".format(self.dorm)
        return s

    def compare(self, other):
        if not super(DftBe, self).compare(other):
            return False
        if self.rate != other.rate:
            # raise Exception("Rates are different {} and {} for {}".format(self.rate, other.rate, self))
            return False
        if self.dorm != other.dorm:
            # raise Exception("Dormancy factors are different {} and {} for {}".format(self.dorm, other.dorm, self))
            return False
        if self.repair != other.repair:
            return False

        return True


class DftGate(DftElement):
    """
    General class for DFT gates.
    """

    def __init__(self, element_id, name, element_type, children, position):
        DftElement.__init__(self, element_id, name, element_type, position)
        assert self.is_gate()
        for child in children:
            self.add_child(child)

    def add_child(self, element):
        """
        Add child.
        :param element: Child to add.
        """
        self.outgoing.append(element)
        element.ingoing.append(self)

    def remove_child(self, element):
        """
        Remove child.
        :param element: Child to remove.
        """
        assert element in self.outgoing
        self.outgoing.remove(element)
        element.remove_parent(self)

    def compare_successors(self, other):
        """
        Check whether two gates have the same successors.
        :param other: Other gate.
        :return: True iff both gates have the same successors.
        """
        if self.element_id == other.element_id:
            return True
        if self.element_type != other.element_type:
            return False
        list_outgoing = [elem.element_id for elem in other.outgoing]
        for element in self.outgoing:
            if element.element_id in list_outgoing:
                list_outgoing.remove(element.element_id)
            else:
                return False
        if len(list_outgoing) > 0:
            return False

        return True

    def get_json(self):
        json = DftElement.get_json(self)
        json['data']['children'] = [str(child.element_id) for child in self.outgoing]
        return json

    def __str__(self):
        return super().__str__() + " with children: " + ", ".join([str(child.name) for child in self.outgoing])


class DftAnd(DftGate):
    """
    AND gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "and", children, position)


class DftOr(DftGate):
    """
    OR gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "or", children, position)


class DftVotingGate(DftGate):
    """
    VOTing gate.
    """

    def __init__(self, element_id, name, voting_threshold, children, position):
        DftGate.__init__(self, element_id, name, "vot", children, position)
        self.votingThreshold = int(voting_threshold)

    def get_json(self):
        json = DftGate.get_json(self)
        json['data']['voting'] = str(self.votingThreshold)
        return json

    def __str__(self):
        return super().__str__() + ", threshold: {}".format(self.votingThreshold)

    def compare(self, other):
        if not super(DftVotingGate, self).compare(other):
            return False
        if self.votingThreshold != other.votingThreshold:
            # raise Exception(
            #    "Threshold are different {} and {} for {}".format(self.votingThreshold, other.votingThreshold, self))
            return False

        return True


class DftPand(DftGate):
    """
    Priority AND gate (PAND).
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "pand", children, position)
        self.isDynamic = True


class DftPor(DftGate):
    """
    Priority OR gate (POR).
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "por", children, position)
        self.isDynamic = True


class DftSpare(DftGate):
    """
    SPARE gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "spare", children, position)
        self.isDynamic = True


class DftDependency(DftGate):
    """
    General class for dependencies (FDEP and PDEP).
    """

    def __init__(self, element_id, name, probability, children, position):
        self.trigger = None
        self.dependent = []
        DftGate.__init__(self, element_id, name, "fdep" if probability == 1 else "pdep", children, position)
        self.probability = probability
        self.isDynamic = True

    def get_json(self):
        json = DftGate.get_json(self)
        if self.probability != 1:
            json['data']['probability'] = str(self.probability)
        return json

    def add_child(self, element):
        if self.trigger is None:
            self.trigger = element
        else:
            self.dependent.append(element)

        self.outgoing.append(element)
        element.ingoing.append(self)

    def remove_last_dep(self):
        """
        Remove the last dependency.
        :return: True iff removal was successful.
        """
        if len(self.dependent) > 1:
            self.dependent.pop()
            return True
        else:
            return False

    def __str__(self):
        return super().__str__() + ", trigger: {} , first dependent element: {}".format(self.trigger.element_id, self.dependent[0].element_id)


class DftSeq(DftGate):
    """
    SEQuence enforcer.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "seq", children, position)
        self.isDynamic = True


class DftMutex(DftGate):
    """
    MUTEX restrictor.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "mutex", children, position)
        self.isDynamic = True
