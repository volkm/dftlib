def create_from_json(json):
    """
    Create DFT element from json.
    :param json: Json.
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

    if element_type == "be":
        # BE
        rate = float(data['rate'])
        dorm = float(data['dorm'])
        repair = float(data['repair'])
        return DftBe(element_id, name, rate, dorm, repair, position)
    elif element_type == "vot":
        # Voting gate
        threshold = int(data['voting'])
        return DftVotingGate(element_id, name, threshold, [], position)
    elif element_type == "fdep":
        # Functional dependency
        return DftDependency(element_id, name, 1, [], position)
    elif element_type == "pdep":
        # Dependency with probability
        if 'probability' in data:
            prob = float(data['probability'])
        else:
            prob = 1
        return DftDependency(element_id, name, prob, [], position)
    elif element_type == "pand":
        # PAND gate
        return DftPandGate(element_id, name, [], position)
    elif element_type == "por":
        # POR gate
        return DftPorGate(element_id, name, [], position)
    elif element_type == "spare":
        # SPARE gate
        return DftSpareGate(element_id, name, [], position)
    else:
        # Gate
        return DftGate(element_id, name, element_type, [], position)


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

    def is_dynamic(self):
        return self.isDynamic

    def is_be(self):
        return self.element_type == "be"

    def is_gate(self):
        return not self.is_be()

    def remove_parent(self, element):
        assert element in self.ingoing
        self.ingoing.remove(element)

    def get_json(self):
        data = dict()
        data['id'] = str(self.element_id)
        data['name'] = str(self.name)
        data['type'] = self.element_type
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
    def __init__(self, element_id, name, element_type, children, position):
        DftElement.__init__(self, element_id, name, element_type, position)
        assert self.is_gate()
        for child in children:
            self.add_child(child)

    def add_child(self, element):
        self.outgoing.append(element)
        element.ingoing.append(self)

    def remove_child(self, element):
        assert element in self.outgoing
        self.outgoing.remove(element)
        element.remove_parent(self)

    def compareSucc(self, other):
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


class DftVotingGate(DftGate):
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


class DftPandGate(DftGate):
    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "pand", children, position)
        self.isDynamic = True


class DftPorGate(DftGate):
    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "por", children, position)
        self.isDynamic = True


class DftSpareGate(DftGate):
    def __init__(self, element_id, name, children, position):
        DftGate.__init__(self, element_id, name, "spare", children, position)
        self.isDynamic = True


class DftDependency(DftGate):
    def __init__(self, element_id, name, probability, children, position):
        DftGate.__init__(self, element_id, name, "fdep", children, position)
        self.trigger = None
        self.dependent = []
        self.probability = probability

    def add_child(self, element):
        if self.trigger is None:
            self.trigger = element
        else:
            self.dependent.append(element)

        self.outgoing.append(element)
        element.ingoing.append(self)

    def remove_last_dep(self):
        if len(self.dependent) > 1:
            self.dependent.pop()
            return True
        else:
            return False

    def __str__(self):
        return super().__str__() + ", trigger: {} , first dependent element: {}".format(self.trigger.element_id, self.dependent[0].element_id)