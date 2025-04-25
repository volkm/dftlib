import json

import dftlib.io.formats as formats
import dftlib.tools.stormpy as stormpy
from dftlib.exceptions.exceptions import DftInvalidArgumentException, DftTypeNotKnownException
from dftlib.storage.dft import Dft
from dftlib.storage.dft_be import BeExponential
from dftlib.storage.dft_gates import DftAnd, DftOr


def parse_dft_galileo_file(file):
    """
    Parse DFT from Galileo file.
    :param file: File.
    :return: DFT.
    """
    # Generate JSON format by converting from Galileo file
    json_obj = stormpy.convert_to_json(file)
    return parse_dft_json(json.loads(json_obj))


def parse_dft_json(json_obj):
    """
    Parse DFT from JSON object.
    :param json_obj: JSON object.
    :return: DFT.
    """
    return Dft(json_obj)


def parse_dft_json_file(file):
    """
    Parse DFT from JSON file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as json_file:
        json_obj = json.load(json_file)
    return parse_dft_json(json_obj)


def parse_dft_json_string(json_string):
    """
    Parse DFT from JSON string.
    :param json_string: JSON string.
    :return: DFT.
    """
    return parse_dft_json(json.loads(json_string))


def parse_dft_txt_string(dft_text):
    """
    Parse DFT from string containing textual description.
    :param dft_text: Textual description of DFT.
    :return: DFT.
    """

    def parse_dft_element_txt(dft, element_text):
        """
        Parse DFT element from string containing textual description.
        :param dft: DFT containing all previously parsed elements.
        :param element_text: Textual description of DFT element.
        :return: DFT element.
        """
        s = element_text.strip()
        pos_opening = s.find("(")
        if pos_opening >= 0:
            # Current level describes a gate
            assert s[-1] == ")"
            gate_type = s[:pos_opening].lower()
            children_text = s[pos_opening + 1 : -1]
            if gate_type == "and":
                gate = DftAnd(dft.next_id(), "And_{}".format(dft.next_id()), [], (0, 0))
            elif gate_type == "or":
                gate = DftOr(dft.next_id(), "Or_{}".format(dft.next_id()), [], (0, 0))
            else:
                raise DftTypeNotKnownException("Gate type '{}' not known.".format(gate_type))
            dft.add(gate)
            # Find splitting points for children
            brackets = 0
            i = 0
            while i < len(children_text):
                if children_text[i] == "(":
                    brackets += 1
                elif children_text[i] == ")":
                    assert brackets > 0
                    brackets -= 1
                elif children_text[i] == "," and brackets == 0:
                    # Can split
                    child_text = children_text[:i]
                    child_element = parse_dft_element_txt(dft, child_text)
                    gate.add_child(child_element)
                    # Keep text for remaining children
                    children_text = children_text[i + 1 :]
                    i = -1  # To account for += 1
                i += 1
            # Handle last child
            child_element = parse_dft_element_txt(dft, children_text)
            gate.add_child(child_element)
            return gate
        else:
            # Complete string is name of BE
            # Check whether BE already exists
            try:
                element = dft.get_element_by_name(s)
            except DftInvalidArgumentException:
                # BE does not exist
                element = None
            if not element:
                # Create new BE
                element = BeExponential(dft.next_id(), s, 1, 1, 0, (0, 0))
                dft.add(element)
            return element

    dft = Dft()
    top_event = parse_dft_element_txt(dft, dft_text)
    dft.set_top_level_element(top_event.element_id)
    return dft


def parse_dft_txt_file(file):
    """
    Parse DFT from textual description in file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as txtFile:
        lines = txtFile.readlines()
        assert len(lines) > 0
        text = lines[0]
    return parse_dft_txt_string(text)


def parse_dft_file(file):
    """
    Parse DFT from file.
    The file can have the following formats: Galileo, JSON, Text.
    :param file: File.
    :return: DFT.
    """
    if formats.is_galileo_file(file):
        return parse_dft_galileo_file(file)
    elif formats.is_json_file(file):
        return parse_dft_json_file(file)
    elif formats.is_text_file(file):
        return parse_dft_txt_file(file)
    else:
        raise DftInvalidArgumentException("File type of '{}' not known.".format(file))
