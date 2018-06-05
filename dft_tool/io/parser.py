import json
import tempfile

from dft_tool.storage.dft import Dft
from dft_tool.tools.storm import Storm
from dft_tool.settings import STORM_PATH


def is_galileo_file(file):
    """
    Checks whether the given file is a DFT in the Galileo format.
    :param file: File.
    :return: True iff the file is a Galileo file.
    """
    return file.endswith(".dft")


def is_json_file(file):
    """
    Checks whether the given file is a DFT in the JSON format.
    :param file: File.
    :return: True iff the file is a JSON file.
    """
    return file.endswith(".json")


def parse_dft_galileo(file):
    """
    Parse DFT from Galileo file.
    :param file: File.
    :return: DFT.
    """
    storm = Storm(STORM_PATH)
    _, tmpjson = tempfile.mkstemp(suffix=".json")
    storm.convert_to_json(file, tmpjson)
    return parse_dft_json(tmpjson)


def parse_dft_json(file):
    """
    Parse DFT from JSON file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as jsonFile:
        dft = Dft(json.load(jsonFile))
    return dft


def parse_dft(file):
    """
    Parse DFT from file.
    The file can have the following formats: Galileo, JSON.
    :param file: File.
    :return: DFT.
    """
    if is_galileo_file(file):
        return parse_dft_galileo(file)
    elif is_json_file(file):
        return parse_dft_json(file)
    else:
        print("ERROR")
