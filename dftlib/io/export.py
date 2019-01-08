import json

from dftlib.storage.dft_elements import *


def export_dft_json(dft, file):
    """
    Export DFT to JSON file.
    :param dft: DFT.
    :param file: File.
    """
    with open(file, 'w') as outFile:
        json.dump(dft.json(), outFile, indent=4)


def galileo_name(element):
    """
    Get name in Galileo format.
    :param element: Element.
    :return: Name as "Name_Id"
    """
    return '"{}"'.format(element.name)


def export_dft_galileo(dft, file):
    """
    Export DFT to Galileo file.
    :param dft: DFT.
    :param file: File.
    """

    # Generate element list in top-down approach
    # TODO make efficient
    elements = []
    queue = [dft.top_level_element]
    while len(queue) > 0:
        element = queue[0]
        queue = queue[1:]
        if element not in elements:
            elements.append(element)
            for child in element.outgoing:
                queue.append(child)

    # Add remaining elements
    for _, element in dft.elements.items():
        if element not in elements:
            elements.append(element)
    assert len(elements) == len(dft.elements)

    # Assert unique names
    names = dict()
    for element in elements:
        assert element.name not in names
        names[element.name] = element

    with open(file, 'w') as out_file:
        out_file.write("toplevel {};\n".format(galileo_name(dft.top_level_element)))
        for element in elements:
            out = galileo_name(element)
            if element.is_be():
                out += " lambda={}".format(element.rate)
                out += " dorm={}".format(element.dorm)
                out_file.write(out + ";\n")
            else:
                assert element.is_gate()
                if isinstance(element, DftVotingGate):
                    out += " vot{}".format(element.votingThreshold)
                elif isinstance(element, DftSpareGate):
                    assert element.element_type == "spare"
                    out += " wsp"
                elif isinstance(element, DftDependency):
                    if element.probability == 1:
                        out += " fdep"
                    else:
                        out += " pdep={}".format(element.probability)
                else:
                    if isinstance(element, DftPandGate):
                        assert element.element_type == "pand"
                    elif isinstance(element, DftPorGate):
                        assert element.element_type == "por"
                    else:
                        assert element.element_type == "and" or element.element_type == "or"
                    out += " " + element.element_type
                for child in element.outgoing:
                    out += " " + galileo_name(child)
                out_file.write(out + ";\n")
