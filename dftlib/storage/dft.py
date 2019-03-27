from dftlib.storage.dft_elements import create_from_json, DftBe, DftGate, DftDependency, DftPandGate, DftPorGate, DftSpareGate


class Dft:
    """
    DFT data structure.
    """

    def __init__(self, json=""):
        self.max_id = 0
        self.position_bounds = [0, 0, 0, 0]  # Left, Top, Right, Bottom
        self.top_level_element = None
        self.elements = {}
        # Parse json
        if json:
            self.from_json(json)

    def from_json(self, json):
        """
        Initialize from Json.
        :param json: Json string.
        """
        # Parse nodes
        for node in json['nodes']:
            element = create_from_json(node)
            self.add(element)

        # Set children
        for node in json['nodes']:
            node_id = node['data']['id']
            element = self.get_element(int(node_id))
            if element.is_gate():
                for child_id in node['data']['children']:
                    element.add_child(self.get_element(int(child_id)))

        # Set trigger for dependencies
        for (_, element) in self.elements.items():
            if isinstance(element, DftDependency):
                element.trigger = element.outgoing[0]

        # Set top level element
        top_level_id = int(json['toplevel'])
        if top_level_id < 0:
            raise Exception("Top level element not defined")
        self.set_top_level_element(top_level_id)

    def count_elements(self):
        return len(self.elements)

    def get_element(self, element_id):
        assert element_id in self.elements
        return self.elements[element_id]

    def get_element_by_name(self, name):
        for (_, element) in self.elements.items():
            if name == element.name:
                return element
        raise Exception("Element {} not known.".format(name))

    def set_top_level_element(self, element_id):
        self.top_level_element = self.get_element(element_id)

    def add(self, element):
        assert element.element_id not in self.elements
        self.elements[element.element_id] = element
        self.max_id = max(self.max_id, element.element_id)
        self.update_bounds(element)

    def remove(self, element):
        assert element.element_id in self.elements
        for parent in element.ingoing:
            parent.remove_child(element)
        for child in element.outgoing:
            child.remove_parent(element)
        del self.elements[element.element_id]

    def update_bounds(self, element):
        self.position_bounds[0] = min(element.position[0], self.position_bounds[0])
        self.position_bounds[1] = min(element.position[1], self.position_bounds[1])
        self.position_bounds[2] = max(element.position[0], self.position_bounds[2])
        self.position_bounds[3] = max(element.position[1], self.position_bounds[3])

    def new_be(self, name, rate, dorm, repair, pos):
        element = DftBe(self.max_id + 1, name, rate, dorm, repair, pos)
        self.add(element)
        return element

    def new_gate(self, name, gate_type, children, pos):
        if gate_type == "pand":
            element = DftPandGate(self.max_id + 1, name, children, pos)
        elif gate_type == "por":
            element = DftPorGate(self.max_id + 1, name, children, pos)
        elif gate_type == "spare":
            element = DftSpareGate(self.max_id + 1, name, children, pos)
        elif gate_type == "fdep":
            element = DftDependency(self.max_id + 1, name, children, pos)
        elif gate_type == "seq":
            element = DftSeqGate(self.max_id + 1, name, children, pos)
        else:
            element = DftGate(self.max_id + 1, name, gate_type, children, pos)
        self.add(element)
        return element

    def json(self):
        data = dict()
        data['toplevel'] = str(self.top_level_element.element_id)
        nodes = []
        for (_, element) in self.elements.items():
            nodes.append(element.get_json())
        data['nodes'] = nodes
        return data

    def statistics(self):
        no_be = 0
        no_dynamic = 0
        for (_, element) in self.elements.items():
            if element.is_be() and element.rate != "0" and element.rate != "0.0":
                no_be += 1
            if element.is_gate() and element.is_dynamic():
                no_dynamic += 1
        return no_be, no_dynamic, len(self.elements)

    def __str__(self):
        no_be, no_dynamic, no_elements = self.statistics()
        return "Dft with {} elements ({} failable BEs, {} dynamic elements), top element: {}".format(no_elements, no_be,
                                                                                                     no_dynamic,
                                                                                                     self.top_level_element.name)

    def get_dynamics(self):
        dynamic_elements = []
        for (_, element) in self.elements.items():
            if element.is_dynamic():
                dynamic_elements.append(element)
        return dynamic_elements

    def verbose_str(self):
        return "{}\n".format(self) + "\n".join([str(element) for (_, element) in self.elements.items()])

    def compare(self, other):
        if not self.top_level_element.compare(other.top_level_element):
            raise Exception(
                "Top level elements {} and {} not equal.".format(self.top_level_element, other.top_level_element))
            return False

        if len(self.elements) != len(other.elements):
            raise Exception(
                "Different number of elements: {} and {}.".format(len(self.elements), len(other.elements)))
            return False

        maximal = max(self.max_id, other.max_id)
        for i in range(0, maximal):
            element = None
            other_element = None
            if i in self.elements:
                element = self.elements[i]
            if i in other.elements:
                other_element = other.elements[i]
            if element is None:
                if other_element is not None:
                    raise Exception("Element with id {} only exists in one.".format(i))
                    return False
            elif other_element is None:
                raise Exception("Element with id {} only exists in one.".format(i))
                return False
            else:
                if not element.compare(other_element):
                    raise Exception(
                        "Elements with id {} are different: {} and {}.".format(i, element, other_element))
                    return False

        return True
