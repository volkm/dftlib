class DftElement:
    """
    Base class for a DFT element.
    """

    def __init__(self, element_id, name, element_type, position):
        self.element_id = element_id
        self.name = name
        self.element_type = element_type
        self.position = position
        self._ingoing = []
        self.relevant = False

    def is_dynamic(self):
        """
        Get whether the element is dynamic.
        :return: True iff element is dynamic.
        """
        return self.element_type not in ["be", "and", "or", "vot"]

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
        assert element in self._ingoing
        self._ingoing.remove(element)

    def parents(self):
        """
        Get parents.
        :return: List of parents.
        """
        return self._ingoing

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
        data["id"] = str(self.element_id)
        data["name"] = str(self.name)
        data["type"] = self.element_type
        if self.relevant:
            data["relevant"] = True
        position = dict()
        position["x"] = self.position[0]
        position["y"] = self.position[1]
        json = {"data": data, "position": position, "group": "nodes"}
        return json

    def __str__(self):
        return "{} - '{}' ({})".format(self.element_type, self.name, self.element_id)

    def compare(self, other, respect_ids):
        """
        Compare elements.
        :param other: Other element.
        :param respect_ids: Whether the ids must be equal.
        :return: True iff both elements are equal.
        """
        if respect_ids:
            if self.element_id != other.element_id:
                return False
        if self.element_type != other.element_type:
            return False

        return True
