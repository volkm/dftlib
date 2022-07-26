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
        # Parse json
        if json:
            self.from_json(json)

    def from_json(self, json):
        """
        Initialize from JSON.
        :param json: JSON object.
        """
        # Parse nodes
        for node in json['nodes']:
            element_type = node['data']['type']
            if element_type == "compound":
                # Compound nodes are ignored
                continue
            elif element_type == "be" or element_type == "be_exp":
                self.add(dft_be.create_from_json(node))
            else:
                self.add(dft_gates.create_from_json(node))

        # Set children
        for node in json['nodes']:
            if node['data']['type'] == "compound":
                # Compound nodes are ignored
                continue
            node_id = node['data']['id']
            element = self.get_element(int(node_id))
            if element.is_gate():
                for child_id in node['data']['children']:
                    element.add_child(self.get_element(int(child_id)))

        # Set top level element
        top_level_id = int(json['toplevel'])
        if top_level_id < 0:
            raise DftInvalidArgumentException("Top level element not defined")
        self.set_top_level_element(top_level_id)

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
        for (_, element) in self.elements.items():
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
        parent_ids = [element.element_id for element in element.ingoing]
        child_ids = [element.element_id for element in element.outgoing]
        for parent_id in parent_ids:
            self.get_element(parent_id).remove_child(element)
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
        data['toplevel'] = str(self.top_level_element.element_id)
        nodes = []
        for (_, element) in self.elements.items():
            nodes.append(element.get_json())
        data['nodes'] = nodes
        return data

    def number_of_be(self):
        """
        Get number of BEs.
        :return: Number of BEs.
        """
        no_be = 0
        for (_, element) in self.elements.items():
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
        for (_, element) in self.elements.items():
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
        return "Dft with {} elements ({} BEs, {} static elements, {} dynamic elements), top element: {}".format(no_elements, no_be, no_static, no_dynamic,
                                                                                                                self.top_level_element.name)

    def verbose_str(self):
        """
        Get verbose string containing information about all elements.
        :return: Verbose string.
        """
        return "{}\n".format(self) + "\n".join([str(element) for (_, element) in self.elements.items()])

    def compare(self, other, respect_ids):
        """
        Compare two DFT.
        :param other: Other DFT.
        :param respect_ids: Whether the ids must be equal.
        :return: True iff all elements, the top-level element and the structure are equal between the two DFTs.
        """
        if not self.top_level_element.compare(other.top_level_element, respect_ids):
            raise Exception("Top level elements {} and {} not equal.".format(self.top_level_element, other.top_level_element))

        if len(self.elements) != len(other.elements):
            raise Exception("Different number of elements: {} and {}.".format(len(self.elements), len(other.elements)))

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
            elif other_element is None:
                raise Exception("Element with id {} only exists in one.".format(i))
            else:
                if not element.compare(other_element, respect_ids):
                    raise Exception("Elements with id {} are different: {} and {}.".format(i, element, other_element))

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
            for child in element.outgoing:
                if child.element_id not in visited:
                    queue.append(child)
                    visited.add(child.element_id)

        # Add remaining elements
        for _, element in self.elements.items():
            if element.element_id not in visited:
                elements.append(element)
        assert len(elements) == len(self.elements)
        return elements
