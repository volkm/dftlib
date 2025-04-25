import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates
from dftlib.exceptions.exceptions import DftTypeNotKnownException, DftInvalidArgumentException


def galileo_name(element):
    """
    Get name in Galileo format.
    :param element: Element.
    :return: Name in quotation marks.
    """
    return '"{}"'.format(element.name)


def export_dft_file(dft, file):
    """
    Export DFT to Galileo file.
    :param dft: DFT.
    :param file: File.
    """
    # Sort topological to ensure that elements are defined before occurring as children
    elements = dft.topological_sort()

    # Assert unique names
    names = dict()
    for element in elements:
        if element.name in names:
            raise DftInvalidArgumentException("Element name '{}' used twice.".format(element.name))
        names[element.name] = element

    # Write file
    with open(file, "w") as out_file:
        # Parameters
        if dft.parametric():
            for param in dft.parameters:
                out_file.write("param {};\n".format(param))
        # Top level event
        out_file.write("toplevel {};\n".format(galileo_name(dft.top_level_element)))
        # DFT elements
        for element in elements:
            if element.is_be():
                out_file.write(export_be_string(element) + ";\n")
            else:
                out_file.write(export_gate_string(element) + ";\n")


def export_gate_string(gate):
    """
    Return DFT gate as string in Galileo format.
    :param gate: DFT gate.
    :return String representing gate.
    """
    assert gate.is_gate()
    s = galileo_name(gate)
    # Handle gate type
    if isinstance(gate, dft_gates.DftAnd):
        s += " and"
    elif isinstance(gate, dft_gates.DftOr):
        s += " or"
    elif isinstance(gate, dft_gates.DftVotingGate):
        s += " vot{}".format(gate.voting_threshold)
    elif isinstance(gate, dft_gates.DftPand):
        s += " pand" + ("" if gate.inclusive else "-excl")
    elif isinstance(gate, dft_gates.DftPor):
        s += " por" + ("" if gate.inclusive else "-excl")
    elif isinstance(gate, dft_gates.DftSpare):
        assert gate.element_type == "spare"
        s += " wsp"
    elif isinstance(gate, dft_gates.DftDependency):
        if gate.probability == 1:
            s += " fdep"
        else:
            s += " pdep={}".format(gate.probability)
    elif isinstance(gate, dft_gates.DftSeq):
        s += " seq"
    elif isinstance(gate, dft_gates.DftMutex):
        s += " mutex"
    else:
        raise DftTypeNotKnownException("Type '{}' not known.".format(gate.element_type))

    # Add children
    for child in gate.children():
        s += " " + galileo_name(child)

    return s


def export_be_string(be):
    """
    Return BE as string in Galileo format.
    :param be: BE.
    :return: String representing BE.
    """
    assert be.is_be()
    s = galileo_name(be)

    # Handle BE type
    if isinstance(be, dft_be.BeConstant):
        s += " prob=" + ("1" if be.failed else "0")
    elif isinstance(be, dft_be.BeProbability):
        s += " prob={}".format(be.probability)
        s += " dorm={}".format(be.dorm)
    elif isinstance(be, dft_be.BeExponential):
        s += " lambda={}".format(be.rate)
        s += " dorm={}".format(be.dorm)
        if be.repair > 0:
            s += " repair={}".format(be.repair)
    elif isinstance(be, dft_be.BeErlang):
        s += " lambda={}".format(be.rate)
        s += " phases={}".format(be.phases)
        s += " dorm={}".format(be.dorm)
    elif isinstance(be, dft_be.BeWeibull):
        s += " shape={}".format(be.shape)
        s += " rate={}".format(be.rate)
    elif isinstance(be, dft_be.BeLognormal):
        s += " mean={}".format(be.mean)
        s += " stddev={}".format(be.stddev)
    else:
        raise DftTypeNotKnownException("BE distribution '{}' not known.".format(be.distribution))

    return s
