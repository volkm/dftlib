import json

from dftlib.exceptions.exceptions import DftTypeNotKnownException, DftInvalidArgumentException
import dftlib.storage.dft_elements as dft_elements


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
    :return: Name in quotation marks.
    """
    return '"{}"'.format(element.name)


def export_dft_galileo(dft, file):
    """
    Export DFT to Galileo file.
    :param dft: DFT.
    :param file: File.
    """
    elements = dft.topological_sort()

    # Assert unique names
    names = dict()
    for element in elements:
        if element.name in names:
            raise DftInvalidArgumentException("Element name '{}' used twice.".format(element.name))
        names[element.name] = element

    with open(file, 'w') as out_file:
        out_file.write("toplevel {};\n".format(galileo_name(dft.top_level_element)))
        for element in elements:
            out = galileo_name(element)
            if element.is_be():
                out += " lambda={}".format(element.rate)
                out += " dorm={}".format(element.dorm)
            else:
                assert element.is_gate()
                # Handle gate type
                if isinstance(element, dft_elements.DftAnd):
                    out += " and"
                elif isinstance(element, dft_elements.DftOr):
                    out += " or"
                elif isinstance(element, dft_elements.DftVotingGate):
                    out += " vot{}".format(element.votingThreshold)
                elif isinstance(element, dft_elements.DftPand):
                    out += " pand"
                elif isinstance(element, dft_elements.DftPor):
                    out += " por"
                elif isinstance(element, dft_elements.DftSpare):
                    assert element.element_type == "spare"
                    out += " wsp"
                elif isinstance(element, dft_elements.DftDependency):
                    if element.probability == 1:
                        out += " fdep"
                    else:
                        out += " pdep={}".format(element.probability)
                elif isinstance(element, dft_elements.DftSeq):
                    out += " seq"
                else:
                    raise DftTypeNotKnownException("Type '{}' not known.".format(element.element_type))
                for child in element.outgoing:
                    out += " " + galileo_name(child)
            out_file.write(out + ";\n")
