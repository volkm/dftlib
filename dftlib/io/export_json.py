import json

from dftlib.storage.dft import Dft


def export_dft_file(dft: Dft, file: str) -> None:
    """
    Export DFT to JSON file.
    :param dft: DFT.
    :param file: File.
    """
    with open(file, "w") as outFile:
        json.dump(dft.json(), outFile, indent=4)


def export_dft_string(dft: Dft, indent: int | None = None):
    """
    Export DFT to JSON string.
    :param dft: DFT.
    :param indent: Indentation level.
    """
    return json.dumps(dft.json(), indent=indent)
