import json
import os
import tempfile

from dftlib.exceptions.exceptions import DftInvalidArgumentException
from dftlib.storage.dft import Dft
from dftlib.tools.storm import Storm


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
    storm = Storm()

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        tmp_file = os.path.join(tmp_dir_name, 'tmp.json')
        storm.convert_to_json(file, tmp_file)
        dft = parse_dft_jso_filen(tmp_file)
    return dft

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
    with open(file) as jsonFile:
        json_obj = json.load(jsonFile)
    return parse_dft_json(json_obj)


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
        return parse_dft_json_file(file)
    else:
        raise DftInvalidArgumentException("File type of '{}' not known.".format(file))
