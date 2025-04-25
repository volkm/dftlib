import dftlib.utility.numbers as numbers
from dftlib.exceptions.exceptions import DftTypeNotKnownException
from dftlib.storage.dft_element import DftElement


def create_from_json(json, parameters=None):
    """
    Create DFT gate from JSON string.
    The children are ignored and must be explicitly set afterwards when all elements are known.
    :param json: JSON string.
    :param parameters: Parameters which are defined. Used for parsing parametric values.
    :return: DFT gate.
    """
    assert json["group"] == "nodes"
    # Parse data from json
    data = json["data"]
    element_id = int(data["id"])
    name = data["name"]
    gate_type = data["type"]
    if "position" in json:
        position = (int(json["position"]["x"]), int(json["position"]["y"]))
    else:
        position = (0, 0)

    if gate_type == "and":
        # AND
        element = DftAnd(element_id, name, [], position)
    elif gate_type == "or":
        # OR
        element = DftOr(element_id, name, [], position)
    elif gate_type == "vot":
        # VOTing gate
        assert "voting" in data
        threshold = int(data["voting"])
        element = DftVotingGate(element_id, name, threshold, [], position)
    elif gate_type == "fdep":
        # Functional dependency (FDEP)
        element = DftDependency(element_id, name, 1, [], position)
    elif gate_type == "pdep":
        # PDEP (dependency with probability)
        assert "probability" in data
        prob = numbers.parse_number(data["probability"], parameters)
        element = DftDependency(element_id, name, prob, [], position)
    elif gate_type == "pand":
        # PAND
        if "inclusive" in data:
            inclusive = bool(data["inclusive"])
        else:
            inclusive = True
        element = DftPand(element_id, name, inclusive, [], position)
    elif gate_type == "por":
        # POR
        if "inclusive" in data:
            inclusive = bool(data["inclusive"])
        else:
            inclusive = True
        element = DftPor(element_id, name, inclusive, [], position)
    elif gate_type == "spare":
        # SPARE
        element = DftSpare(element_id, name, [], position)
    elif gate_type == "seq":
        # Sequence enforcer
        element = DftSeq(element_id, name, [], position)
    elif gate_type == "mutex":
        # Mutex
        element = DftMutex(element_id, name, [], position)
    else:
        raise DftTypeNotKnownException("Gate type '{}' not known.".format(gate_type))

    if "relevant" in data:
        element.relevant = bool(data["relevant"])
    return element


class DftGate(DftElement):
    """
    Base class for DFT gates.
    """

    def __init__(self, element_id, name, element_type, children, position):
        DftElement.__init__(self, element_id, name, element_type, position)
        assert self.is_gate()
        self._outgoing = []
        for child in children:
            self.add_child(child)

    def add_child(self, element):
        """
        Add child.
        :param element: Child to add.
        """
        self._outgoing.append(element)
        element._ingoing.append(self)

    def remove_child(self, element):
        """
        Remove child.
        :param element: Child to remove.
        """
        assert element in self._outgoing
        self._outgoing.remove(element)
        element.remove_parent(self)

    def replace_child(self, child, element):
        """
        Replace given child with new element.
        Maintains the order.
        :param child: Original child to be replaced.
        :param element: Element which will be the new child.
        """
        index = self._outgoing.index(child)  # A ValueError is raised if the child was not found
        self._outgoing[index] = element
        child.remove_parent(self)
        element._ingoing.append(self)

    def children(self):
        """
        Get children.
        :return: Ordered list of children.
        """
        return self._outgoing

    def compare_successors(self, other, ordered, respect_ids):
        """
        Check whether two gates have the same successors.
        :param other: Other gate.
        :param ordered: Whether the order of successors should be respected.
        :param respect_ids: Whether the ids of the successors must be equal.
        :return: True iff both gates have the same successors.
        """
        if len(self.children()) != len(other.children()):
            return False

        if ordered:
            for i in range(len(self.children())):
                if not self.children()[i].compare(other.children()[i], respect_ids):
                    return False
            return True
        else:
            # Use either id or name as unique identifier
            map_children = {elem.element_id if respect_ids else elem.name: elem for elem in other.children()}
            for element in self.children():
                identifier = element.element_id if respect_ids else element.name
                if identifier in map_children:
                    if element.compare(map_children[identifier], respect_ids):
                        # Found matching successor
                        del map_children[identifier]
                    else:
                        # Not matching
                        return False
                else:
                    # Found no matching successor in other
                    return False

            assert len(map_children) == 0
            return True

    def get_json(self):
        json = DftElement.get_json(self)
        json["data"]["children"] = [str(child.element_id) for child in self.children()]
        return json

    def __str__(self):
        return super().__str__() + " with children: " + ", ".join([str(child.name) for child in self.children()])


class DftAnd(DftGate):
    """
    AND gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "and", children, position)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        return self.compare_successors(other, ordered=False, respect_ids=respect_ids)


class DftOr(DftGate):
    """
    OR gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "or", children, position)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        return self.compare_successors(other, ordered=False, respect_ids=respect_ids)


class DftVotingGate(DftGate):
    """
    VOTing gate.
    """

    def __init__(self, element_id, name, voting_threshold, children, position):
        DftGate.__init__(self, element_id, name, "vot", children, position)
        self.voting_threshold = int(voting_threshold)

    def get_json(self):
        json = DftGate.get_json(self)
        json["data"]["voting"] = str(self.voting_threshold)
        return json

    def __str__(self):
        return super().__str__() + ", threshold: {}".format(self.voting_threshold)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        if not self.compare_successors(other, ordered=False, respect_ids=respect_ids):
            return False

        return self.voting_threshold == other.voting_threshold


class DftPriorityGate(DftGate):
    """
    Base class for priority gates.
    """

    def __init__(self, element_id, name, element_type, inclusive, children, position):
        DftGate.__init__(self, element_id, name, element_type, children, position)
        self.inclusive = inclusive

    def get_json(self):
        json = DftGate.get_json(self)
        json["data"]["inclusive"] = self.inclusive
        return json

    def __str__(self):
        return super().__str__() + ", {}".format("inclusive" if self.inclusive else "exclusive")

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        if not self.compare_successors(other, ordered=True, respect_ids=respect_ids):
            return False

        return self.inclusive == other.inclusive


class DftPand(DftPriorityGate):
    """
    Priority AND gate (PAND).
    """

    def __init__(self, element_id, name, inclusive, children, position):
        DftPriorityGate.__init__(self, element_id, name, "pand", inclusive, children, position)


class DftPor(DftPriorityGate):
    """
    Priority OR gate (POR).
    """

    def __init__(self, element_id, name, inclusive, children, position):
        DftPriorityGate.__init__(self, element_id, name, "por", inclusive, children, position)


class DftSpare(DftGate):
    """
    SPARE gate.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "spare", children, position)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        return self.compare_successors(other, ordered=True, respect_ids=respect_ids)


class DftDependency(DftGate):
    """
    General class for dependencies (FDEP and PDEP).
    """

    def __init__(self, element_id, name, probability, children, position):
        DftGate.__init__(self, element_id, name, "fdep" if probability == 1 else "pdep", children, position)
        self.probability = probability

    def get_json(self):
        json = DftGate.get_json(self)
        if self.probability != 1:
            json["data"]["probability"] = str(self.probability)
        return json

    def trigger(self):
        if self.children():
            return self.children()[0]
        else:
            return None

    def dependent(self):
        return self.children()[1:]

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        if not self.compare_successors(other, ordered=False, respect_ids=respect_ids):
            return False
        # Compare trigger
        if not self.trigger().compare(other.trigger(), respect_ids):
            return False

        return self.probability == other.probability

    def __str__(self):
        return super().__str__() + (", probability: {}".format(self.probability) if self.probability != 1 else "")


class DftSeq(DftGate):
    """
    SEQuence enforcer.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "seq", children, position)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        return self.compare_successors(other, ordered=True, respect_ids=respect_ids)


class DftMutex(DftGate):
    """
    MUTEX restrictor.
    """

    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "mutex", children, position)

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False

        return self.compare_successors(other, ordered=False, respect_ids=respect_ids)
