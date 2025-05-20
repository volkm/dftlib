import dftlib.storage.dft_be as dft_be
import dftlib.storage.dft_gates as dft_gates
from dftlib.exceptions.exceptions import DftTypeNotKnownException, DftTypeNotSupportedException


def generate_tikz_node(element, is_tle=False):
    s = ""
    name = element.name
    # Set position information
    pos_x, pos_y = element.position[0] / 75, -element.position[1] / 75
    pos_x, pos_y = round(pos_x, 1), round(pos_y, 1)
    position = "({}, {})".format(pos_x, pos_y)

    # Set node type
    no_children = 0
    if not element.is_be():
        if len(element.children()) > 6:
            raise DftTypeNotSupportedException("More than 6 children (for element '{}') are currently not supported for tikz export.".format(element.name))
        else:
            no_children = str(len(element.children()))

    if element.is_be():
        if isinstance(element, dft_be.BeConstant):
            node_type = "cnst"
        else:
            node_type = "be"
    elif isinstance(element, dft_gates.DftAnd) or isinstance(element, dft_gates.DftVotingGate) or isinstance(element, dft_gates.DftPand):
        node_type = "and" + no_children
    elif isinstance(element, dft_gates.DftOr) or isinstance(element, dft_gates.DftPor):
        node_type = "or" + no_children
    elif isinstance(element, dft_gates.DftSpare):
        node_type = "spare"
    elif isinstance(element, dft_gates.DftDependency):
        node_type = "fdep"
    elif isinstance(element, dft_gates.DftSeq):
        node_type = "seq"
    elif isinstance(element, dft_gates.DftMutex):
        node_type = "mutex"
    else:
        raise DftTypeNotKnownException("Type '{}' not known.".format(element.element_type))

    # Add node
    label_node = ""
    if isinstance(element, dft_gates.DftVotingGate):
        label_node = "\\rotatebox{{270}}{{${}$}}".format(element.voting_threshold)
    elif isinstance(element, dft_be.BeConstant):
        label_node = "$\\top$" if element.failed else "$\\bot$"
    s += "\t\\node[{}] ({}) at {} {{{}}};\n".format(node_type, name, position, label_node)

    # Add triangles for PAND or POR
    if isinstance(element, dft_gates.DftPand):
        s += "\t\\node[triangle_pand] (triangle_{0}) at({0}) {{}};\n".format(name)
    elif isinstance(element, dft_gates.DftPor):
        s += "\t\\node[triangle_por] (triangle_{0}) at({0}) {{}};\n".format(name)

    # Add labelbox for all elements
    label_anchor = "north"
    if (
        isinstance(element, dft_gates.DftAnd)
        or isinstance(element, dft_gates.DftOr)
        or isinstance(element, dft_gates.DftVotingGate)
        or isinstance(element, dft_gates.DftPand)
        or isinstance(element, dft_gates.DftPor)
    ):
        label_anchor = "east"
    label = name
    # Replace underscores
    label = label.replace("_", r"\_")
    if is_tle:
        label = "\\underline{{{}}}".format(label)
    s += "\t\\node[labelbox] ({0}_label) at ({0}.{1}) {{{2}}};\n".format(name, label_anchor, label)

    # Add ratebox for BEs
    if element.is_be():
        if isinstance(element, dft_be.BeExponential):
            if element.dorm < 1:
                label = "\\ratelabel{{{0}}}{{{1}}}".format(element.rate, element.rate * element.dorm)
            else:
                label = "\\rateactlabel{{{0}}}".format(element.rate)
            s += "\t\\node[ratebox] ({0}_rate) at ({0}.south) {{{1}}};\n".format(name, label)
        elif isinstance(element, dft_be.BeProbability):
            if element.dorm < 1:
                label = "\\problabel{{{0}}}{{{1}}}".format(element.probability, element.probability * element.dorm)
            else:
                label = "\\probactlabel{{{0}}}".format(element.probability)
            s += "\t\\node[ratebox] ({0}_prob) at ({0}.south) {{{1}}};\n".format(name, label)
        elif isinstance(element, dft_be.BeConstant):
            pass
        else:
            raise DftTypeNotSupportedException("BE distribution '{}' not supported for tikz export.".format(element.distribution))

    # Add probability for PDEP
    if isinstance(element, dft_gates.DftDependency) and element.probability < 1:
        s += "\t\\node[above=0cm of {0}.center] ({0}_p) {{${1}$}};\n".format(name, element.probability)

    return s


SPARE_CHILDREN = {
    1: "P",
    2: "SA",
    3: "SB",
    4: "SC",
    5: "SD",
    6: "SE",
}
FDEP_CHILDREN = {
    1: "T",
    2: "EA",
    3: "EB",
    4: "EC",
    5: "ED",
    6: "EE",
}


def generate_tikz_edges(element):
    s = ""

    if element.is_gate():
        assert element.is_gate()
        no_children = len(element.children())
        assert no_children <= 6
        # Handle gate type

        i = 1
        for child in element.children():
            if (
                isinstance(element, dft_gates.DftAnd)
                or isinstance(element, dft_gates.DftOr)
                or isinstance(element, dft_gates.DftVotingGate)
                or isinstance(element, dft_gates.DftPand)
                or isinstance(element, dft_gates.DftPor)
            ):
                s += "\t\\draw[-]({}.input {}) -- ({}_label.north);\n".format(element.name, i, child.name)
                i += 1
            elif isinstance(element, dft_gates.DftSpare):
                s += "\t\\draw[-]({}.{}) -- ({}_label.north);\n".format(element.name, SPARE_CHILDREN[i], child.name)
                i += 1
            elif isinstance(element, dft_gates.DftDependency):
                s += "\t\\draw[-]({}.{}) -- ({}_label.north);\n".format(element.name, FDEP_CHILDREN[i], child.name)
                i += 1
            elif isinstance(element, dft_gates.DftSeq) or isinstance(element, dft_gates.DftMutex):
                if no_children == 2:
                    seq_children = {1: 250, 2: 290}
                elif no_children == 3:
                    seq_children = {1: 250, 2: 270, 3: 290}
                elif no_children == 4:
                    seq_children = {1: 250, 2: 265, 3: 275, 4: 290}
                elif no_children == 5:
                    seq_children = {1: 250, 2: 260, 3: 270, 4: 280, 5: 290}
                else:
                    raise DftTypeNotSupportedException(
                        "{} children (for element '{}') are currently not supported for tikz export.".format(no_children, element.name)
                    )
                s += "\t\\draw[-]({}.{}) -- ({}_label.north);\n".format(element.name, seq_children[i], child.name)
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

    with open(file, "w") as f:
        f.write("\\begin{tikzpicture}\n")

        # Draw nodes
        for elem in elements:
            f.write(generate_tikz_node(elem, tle_id == elem.element_id))

        f.write("\n")

        # Draw edges
        for elem in elements:
            f.write(generate_tikz_edges(elem))

        f.write("\\end{tikzpicture}\n")
