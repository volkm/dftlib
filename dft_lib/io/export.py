import json


def export_dft_json(dft, file):
    """
    Export DFT to JSON file.
    :param dft: DFT.
    :param file: File.
    """
    with open(file, 'w') as outFile:
        json.dump(dft.json(), outFile, indent=4)
