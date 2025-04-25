import json


def export_dft_file(dft, file):
    """
    Export DFT to JSON file.
    :param dft: DFT.
    :param file: File.
    """
    with open(file, "w") as outFile:
        json.dump(dft.json(), outFile, indent=4)


def export_dft_string(dft, indent=None):
    """
    Export DFT to JSON string.
    :param dft: DFT.
    :param indent: Indentation level.
    """
    return json.dumps(dft.json(), indent=indent)
