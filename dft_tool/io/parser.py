import json

from dft_tool.storage.dft import Dft


def parse_dft_json(file):
    """
    Parse DFT from JSON file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as jsonFile:
        dft = Dft(json.load(jsonFile))
    return dft
