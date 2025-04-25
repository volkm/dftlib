import dftlib.storage.dft_gates as dft_gates
from dftlib.exceptions.exceptions import DftInvalidArgumentException, DftTypeNotSupportedException


def export_dft_string(dft):
    """
    Export DFT as textual description.
    :param dft: DFT.
    :return: DFT as textual description.
    """
    exported_elements = dict()
    next_be_id = 0

    def export_element_string(element):
        """
        Export DFT element (and its subtree) as string.
        The method recursively exports the children.
        :param element: Element.
        :return: Textual description of element and its subtree.
        """
        # Access to variables in parent scope
        nonlocal exported_elements
        nonlocal next_be_id

        if element.element_id in exported_elements:
            # Element was already exported before -> use existing textual description
            return exported_elements[element.element_id]
        else:
            if element.is_be():
                # Export BE by id
                s = "BE{}".format(next_be_id)
                next_be_id += 1
            else:
                assert element.is_gate()
                # Recursively export children of gate
                child_strings = []
                for child in element.children():
                    child_strings.append(export_element_string(child))
                if not (isinstance(element, dft_gates.DftAnd) or isinstance(element, dft_gates.DftOr)):
                    raise DftTypeNotSupportedException("DFT element {} of type {} not supported in export.".format(element, element.element_type))
                s = element.element_type.upper() + "(" + ",".join(child_strings) + ")"
            exported_elements[element.element_id] = s
            return s

    dft_string = export_element_string(dft.top_level_element)
    assert next_be_id == dft.number_of_be()
    return dft_string


def export_dft_file(dft, file):
    """
    Export DFT to textual format in file.
    :param dft: DFT.
    :param file: File.
    """
    # Write file
    with open(file, "w") as out_file:
        # Parameters
        if dft.parametric():
            raise DftInvalidArgumentException("Parameters are not supported in export.")
        # Top level event
        out_file.write(export_dft_string(dft))
