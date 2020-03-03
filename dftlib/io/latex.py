from dftlib.exceptions.exceptions import DftTypeNotKnownException, DftInvalidArgumentException, DftTypeNotSupportedException
import dftlib.storage.dft_elements as dft_elements


def generate_tikz_node(element, is_tle=False):
    s = ""
    name = element.name
    position = "({}, {})".format(element.position[0] / 75, -element.position[1] / 75)

    # Set node type
    if not element.is_be():
        if len(element.outgoing) > 6:
            raise DftTypeNotSupportedException("More than 6 children (for element '{}') are currently not supported for tikz export.".format(element.name))
        else:
            no_children = str(len(element.outgoing))

    if element.is_be():
        node_type = "be"
    elif isinstance(element, dft_elements.DftAnd) or isinstance(element, dft_elements.DftVotingGate) or isinstance(element, dft_elements.DftPand):
        node_type = "and" + no_children
    elif isinstance(element, dft_elements.DftOr) or isinstance(element, dft_elements.DftPor):
        node_type = "or" + no_children
    elif isinstance(element, dft_elements.DftSpare):
        node_type = "spare"
    elif isinstance(element, dft_elements.DftDependency):
        node_type = "fdep"
    elif isinstance(element, dft_elements.DftSeq):
        node_type = "seq"
    else:
        raise DftTypeNotKnownException("Type '{}' not known.".format(element.element_type))

    # Add node
    label_node = ""
    if isinstance(element, dft_elements.DftVotingGate):
        label_node = "\\rotatebox{{270}}{{${}$}}".format(element.votingThreshold)
    s += "\\node[{}] ({}) at {} {{{}}};\n".format(node_type, name, position, label_node)

    # Add triangles for PAND or POR
    if isinstance(element, dft_elements.DftPand):
        s += "\\node[triangle, scale = 1.62, yshift = -3.5, xscale = 0.80] (triangle_{0}) at({0}) {{}};\n".format(name)
    elif isinstance(element, dft_elements.DftPor):
        s += "\\node[btriangle, scale = 1.62, yscale = 0.915, xshift = -0.113cm] (triangle_{0}) at({0}) {{}};\n".format(name)

    # Add labelbox
    label_anchor = "north"
    if isinstance(element, dft_elements.DftAnd) or isinstance(element, dft_elements.DftOr) \
            or isinstance(element, dft_elements.DftVotingGate) or isinstance(element, dft_elements.DftPand) \
            or isinstance(element, dft_elements.DftPor):
        label_anchor = "east"
    label = name
    if is_tle:
        label = "\\underline{{{}}}".format(name)
    s += "\\node[labelbox] ({0}_label) at ({0}.{1}) {{{2}}};\n".format(name, label_anchor, label)

    return s


SPARE_CHILDREN = {
    1: "P", 2: "SA", 3: "SB", 4: "SC", 5: "SD", 6: "SE",
}
FDEP_CHILDREN = {
    1: "T", 2: "EA", 3: "EB", 4: "EC", 5: "ED", 6: "EE",
}


def generate_tikz_edges(element):
    s = ""

    if element.is_be():
        assert not element.outgoing
    else:
        assert element.is_gate()
        assert len(element.outgoing) <= 6
        # Handle gate type

        i = 1
        for child in element.outgoing:
            if isinstance(element, dft_elements.DftAnd) or isinstance(element, dft_elements.DftOr) \
                    or isinstance(element, dft_elements.DftVotingGate) or isinstance(element, dft_elements.DftPand) \
                    or isinstance(element, dft_elements.DftPor):
                s += "\\draw[-]({}.input {}) -- ({}_label.north);\n".format(element.name, i, child.name)
                i += 1
            elif isinstance(element, dft_elements.DftSpare):
                s += "\\draw[-]({}.input {}) -- ({}_label.north);\n".format(element.name, SPARE_CHILDREN[i], child.name)
                i += 1
            elif isinstance(element, dft_elements.DftDependency):
                s += "\\draw[-]({}.input {}) -- ({}_label.north);\n".format(element.name, FDEP_CHILDREN[i], child.name)
                i += 1
            elif isinstance(element, dft_elements.DftSeq):
                s += "\\draw[-]({}.input {}) -- ({}_label.north);\n".format(element.name, i, child.name)
                i += 1
            else:
                raise DftTypeNotKnownException("Type '{}' not known.".format(element.element_type))

    return s


def generate_tikz(dft, file):
    """
    Generate tikz file from DFT.
    :param dft: DFT.
    :param file: Output tikz file.
    """
    elements = dft.topological_sort()
    tle_id = dft.top_level_element.element_id

    with open(file, 'w') as f:
        f.write("\\begin{tikzpicture}\n")

        # Draw nodes
        for elem in elements:
            f.write(generate_tikz_node(elem, tle_id == elem.element_id))

        # Draw edges
        for elem in elements:
            f.write(generate_tikz_edges(elem))

        f.write("\\end{tikzpicture}\n")
