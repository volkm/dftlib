import json

from dft_lib.storage.dft import Dft


def parse_dft_json(file):
    """
    Parse DFT from JSON file.
    :param file: File.
    :return: DFT.
    """
    with open(file) as jsonFile:
        dft = Dft(json.load(jsonFile))
    return dft

def parse_dft_json_string(string):
	"""
	Parse DFT from JSON string.
	:param file: File.
	:return: DFT.
	"""
	dft = Dft(string)
	return dft