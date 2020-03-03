import json
import tempfile

from dftlib.storage.dft import Dft
from dftlib.tools.storm import Storm
import dftlib._config as config
from dftlib.exceptions.exceptions import ToolNotFound, DftInvalidArgumentException


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

    if config.has_storm_dft:
        storm = Storm(config.storm_path)
        _, tmpjson = tempfile.mkstemp(suffix=".json")
        storm.convert_to_json(file, tmpjson)
        return parse_dft_json(tmpjson)
    else:
        raise ToolNotFound("Path of binary 'storm-dft' not specified.")


def parse_dft_json_string(string):
    """
    Parse DFT from JSON string.
    :param file: File.
    :return: DFT.
    """
    dft = Dft(string)
    return dft


def parse_dft_json(file):
    """
    Parse DFT from JSON file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as jsonFile:
        json_string = json.load(jsonFile)
    return parse_dft_json_string(json_string)


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
        raise DftInvalidArgumentException("File type of '{}' not known.".format(file))
