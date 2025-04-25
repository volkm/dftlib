from collections import deque

import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates
from dftlib.exceptions.exceptions import DftInvalidArgumentException
from dftlib.storage.dft_element import DftElement


class Dft:
    """
    DFT data structure.
    """

    def __init__(self, json=""):
        self.max_id = -1
        self.position_bounds = [0, 0, 0, 0]  # Left, Top, Right, Bottom
        self.top_level_element = None
        self.elements = {}
        self.parameters = None
        # Parse json
        if json:
            self.from_json(json)

    def from_json(self, json):
        """
        Initialize from JSON.
        :param json: JSON object.
        """
        # Parse (optional) parameters
        if "parameters" in json and len(json["parameters"]) > 0:
            self.parameters = []
            for param in json["parameters"]:
                assert param not in self.parameters
                self.parameters.append(param)
        # Parse nodes
        for node in json["nodes"]:
            element_type = node["data"]["type"]
            if element_type == "compound":
                # Compound nodes are ignored
                continue
            elif element_type == "be" or element_type == "be_exp":
                self.add(dft_be.create_from_json(node, self.parameters))
            else:
                self.add(dft_gates.create_from_json(node, self.parameters))

        # Set children
        for node in json["nodes"]:
            if node["data"]["type"] == "compound":
                # Compound nodes are ignored
                continue
            node_id = node["data"]["id"]
            element = self.get_element(int(node_id))
            if element.is_gate():
                for child_id in node["data"]["children"]:
                    element.add_child(self.get_element(int(child_id)))

        # Set top level element
        top_level_id = int(json["toplevel"])
        if top_level_id < 0:
            raise DftInvalidArgumentException("Top level element not defined")
        self.set_top_level_element(top_level_id)
        assert self.is_valid()

    def parametric(self):
        """
        Return whether the DFT contains parameters.
        :return: True iff parameters are defined.
        """
        return self.parameters is not None

    def has_parameter(self, name):
        """
        Check whether the given parameter is known.
        :param name: Name of the parameter.
        :return: True iff parameter was defined before.
        """
        assert self.parametric()
        return name in self.parameters

    def next_id(self):
        return self.max_id + 1

    def size(self):
        """
        Get number of elements (gates + BEs)
        :return: Number of elements.
        """
        return len(self.elements)

    def get_element(self, element_id):
        """
        Get element by id.
        :param element_id: Id.
        :return: Element.
        """
        if element_id not in self.elements:
            raise DftInvalidArgumentException("Element with id {} not known.".format(element_id))
        return self.elements[element_id]

    def get_element_by_name(self, name):
        """
        Get element by name.
        :param name: Name.
        :return: Element.
        """
        for element in self.elements.values():
            if name == element.name:
                return element
        raise DftInvalidArgumentException("Element {} not known.".format(name))

    def set_top_level_element(self, element_id):
        """
        Set top level element.
        :param element_id: Id.
        """
        self.top_level_element = self.get_element(element_id)
        self.top_level_element.set_relevant(True)

    def add(self, element):
        """
        Add element.
        :param element: Element.
        """
        assert isinstance(element, DftElement)
        assert element.element_id not in self.elements
        self.elements[element.element_id] = element
        self.max_id = max(self.max_id, element.element_id)
        self.update_bounds(element)

    def remove(self, element):
        """
        Remove element.
        :param element: Element.
        """
        assert element.element_id in self.elements
        # Remember ids for iteration
        # Otherwise we are iterating over the list we are also removing from
        parent_ids = [element.element_id for element in element.parents()]
        for parent_id in parent_ids:
            self.get_element(parent_id).remove_child(element)
        if element.is_gate():
            child_ids = [element.element_id for element in element.children()]
            for child_id in child_ids:
                self.get_element(child_id).remove_parent(element)
        del self.elements[element.element_id]

    def update_bounds(self, element):
        """
        Update position bounds by also including bounds of given element.
        :param element: Element.
        """
        self.position_bounds[0] = min(element.position[0], self.position_bounds[0])
        self.position_bounds[1] = min(element.position[1], self.position_bounds[1])
        self.position_bounds[2] = max(element.position[0], self.position_bounds[2])
        self.position_bounds[3] = max(element.position[1], self.position_bounds[3])

    def json(self):
        """
        Get JSON string for DFT.
        :return: JSON string.
        """
        data = dict()
        data["toplevel"] = str(self.top_level_element.element_id)
        if self.parametric():
            data["parameters"] = self.parameters
        nodes = []
        for element in self.elements.values():
            nodes.append(element.get_json())
        data["nodes"] = nodes
        return data

    def number_of_be(self):
        """
        Get number of BEs.
        :return: Number of BEs.
        """
        no_be = 0
        for element in self.elements.values():
            if element.is_be():
                no_be += 1
        return no_be

    def statistics(self):
        """
        Get general statistics about DFT.
        :return: Tuple (number of BEs, number of static gates, number of dynamic gates, number of elements)
        """
        no_be = 0
        no_static = 0
        no_dynamic = 0
        for element in self.elements.values():
            if element.is_be():
                no_be += 1
            else:
                assert element.is_gate()
                if element.is_dynamic():
                    no_dynamic += 1
                else:
                    no_static += 1
        assert no_static + no_dynamic + no_be == len(self.elements)
        return no_be, no_static, no_dynamic, len(self.elements)

    def __str__(self):
        no_be, no_static, no_dynamic, no_elements = self.statistics()
        return "Dft with {} elements ({} BEs, {} static elements, {} dynamic elements), top element: {}".format(
            no_elements, no_be, no_static, no_dynamic, self.top_level_element.name
        )

    def verbose_str(self):
        """
        Get verbose string containing information about all elements.
        :return: Verbose string.
        """
        return "{}\n".format(self) + "\n".join([str(element) for element in self.elements.values()])

    def compare(self, other, respect_ids):
        """
        Compare two DFT.
        Note that the comparison currently performs redundant work as for each element comparison the complete subtree is checked.
        :param other: Other DFT.
        :param respect_ids: Whether the ids must be equal.
        :return: True iff all elements, the top-level element and the structure are equal between the two DFTs.
        """
        if len(self.elements) != len(other.elements):
            raise Exception("Different number of elements: {} and {}.".format(len(self.elements), len(other.elements)))

        if respect_ids:
            if self.max_id != other.max_id:
                raise Exception("Different maximal ids: {} and {} .".format(self.max_id, other.max_id))
            for i in range(0, self.max_id):
                assert i in self.elements
                element = self.elements[i]
                assert i in other.elements
                other_element = other.elements[i]
                if not element.compare(other_element, respect_ids):
                    raise Exception("Elements with id {} are different: {} and {}.".format(i, element, other_element))
        else:
            # Prepare mapping from name to id (for other DFT)
            # because ids could be different between both DFTs
            other_mapping = dict()
            for element in other.elements.values():
                assert element.name not in other_mapping
                other_mapping[element.name] = element

            for element in self.elements.values():
                if element.name not in other_mapping:
                    raise Exception("Element {} not present in other DFT.".format(element))
                other_element = other_mapping[element.name]
                if not element.compare(other_element, respect_ids):
                    raise Exception("Elements are different: {} and {}.".format(element, other_element))

        if not self.top_level_element.compare(other.top_level_element, respect_ids):
            raise Exception("Top level elements {} and {} not equal.".format(self.top_level_element, other.top_level_element))

        return True

    def topological_sort(self):
        """
        Return the elements in topological sorting from top to bottom.
        :return: List of elements.
        """
        elements = []
        visited = set()
        queue = deque()
        queue.append(self.top_level_element)
        visited.add(self.top_level_element.element_id)
        while len(queue) > 0:
            element = queue.popleft()
            elements.append(element)
            if element.is_be():
                continue
            for child in element.children():
                if child.element_id not in visited:
                    queue.append(child)
                    visited.add(child.element_id)

        # Add remaining elements
        for element in self.elements.values():
            if element.element_id not in visited:
                elements.append(element)
        assert len(elements) == len(self.elements)
        return elements

    def get_module(self, module_repr):
        """
        Compute module of module_repr.
        :param module_repr: Module representative.
        :return: List of element ids which form the module for module_repr.
        """
        # Check if module_repr is a valid module representative (either top level element or SPARE-gate)
        if module_repr.element_id != self.top_level_element.element_id and not isinstance(module_repr, dft_gates.DftSpare):
            return []

        # Compute module
        module = []
        visited = set()
        queue = deque()
        queue.append(module_repr)
        visited.add(module_repr.element_id)
        while len(queue) > 0:
            elem = queue.popleft()
            module.append(elem.element_id)
            # Go "downwards" and only stop when encountering a BE or a SPARE
            if not elem.is_be() and not isinstance(elem, dft_gates.DftSpare):
                for child in elem.children():
                    if child.element_id not in visited:
                        queue.append(child)
                        visited.add(child.element_id)
            # Go "sideways" for dependencies and SEQ/MUTEX
            for parent in elem.parents():
                if parent.element_id not in visited:
                    if isinstance(elem, dft_gates.DftDependency) or isinstance(elem, dft_gates.DftSeq) or isinstance(elem, dft_gates.DftMutex):
                        queue.append(parent)
                        visited.add(parent)
        return module

    def is_valid(self):
        """
        Checks whether the DFT is valid, e.g. acyclic, has TLE, etc.
        DFTs should be well-formed.
        :return: True iff the DFT is valid.
        """
        if self.size() > self.max_id + 1:
            return False
        if not self.top_level_element:
            return False
        if self.is_cyclic():
            return False
        return True

    def is_cyclic(self):
        """
        Checks whether the DFT is cyclic.
        DFTs should be acyclic.
        :return: True iff the DFT has a cycle (excluding dependencies and restrictors).
        """

        def dfs(element):
            if finished[element.element_id]:
                return False
            if visited[element.element_id]:
                # Found cycle
                return True
            visited[element.element_id] = True
            if (
                not element.is_be()
                and not isinstance(element, dft_gates.DftDependency)
                and not isinstance(element, dft_gates.DftSeq)
                and not isinstance(element, dft_gates.DftMutex)
            ):
                # BEs, dependencies and restrictors are skipped
                for child in element.children():
                    if dfs(child):
                        return True
            finished[element.element_id] = True
            return False

        # Check for cycle via DFS
        visited = [False] * self.next_id()
        finished = [False] * self.next_id()
        for elem in self.elements.values():
            if dfs(elem):
                return True
        return False
