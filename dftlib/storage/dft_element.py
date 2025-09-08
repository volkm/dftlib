from enum import StrEnum


class ElementType(StrEnum):
    BE = "be"
    AND = "and"
    OR = "or"
    VOT = "vot"
    PAND = "pand"
    POR = "por"
    SPARE = "spare"
    FDEP = "fdep"
    PDEP = "pdep"
    SEQ = "seq"
    MUTEX = "mutex"


class DftElement:
    """
    Base class for a DFT element.
    """

    def __init__(self, element_id: int, name: str, element_type: ElementType, position: tuple[float, float]) -> None:
        self.element_id: int = element_id
        self.name: str = name
        self.element_type: ElementType = element_type
        self.position: tuple[float, float] = position
        self._ingoing: list[DftElement] = []
        self.relevant: bool = False

    def is_dynamic(self) -> bool:
        """
        Get whether the element is dynamic.
        :return: True iff element is dynamic.
        """
        return self.element_type not in [ElementType.BE, ElementType.AND, ElementType.OR, ElementType.VOT]

    def is_be(self) -> bool:
        """
        Get whether the element is a BE.
        :return: True iff element is a BE.
        """
        return self.element_type == ElementType.BE

    def is_gate(self) -> bool:
        """
        Get whether the element is a gate.
        :return: True iff element is a gate.
        """
        return not self.is_be()

    def remove_parent(self, element: "DftElement") -> None:
        """
        Remove parent.
        :param element: Parent to remove.
        """
        assert element in self._ingoing
        self._ingoing.remove(element)

    def parents(self) -> list["dftlib.storage.dft_gates.DftGate"]:
        """
        Get parents.
        :return: List of parents.
        """
        return self._ingoing

    def set_relevant(self, relevant: bool = True) -> None:
        """
        Set whether the element is relevant (and will not be set to 'Don't Care' for example).
        :param relevant: Whether the element is relevant.
        """
        self.relevant = relevant

    def get_json(self) -> dict:
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

    def __str__(self) -> str:
        return "{} - '{}' ({})".format(self.element_type, self.name, self.element_id)

    def compare(self, other: "DftElement", respect_ids: bool) -> bool:
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
