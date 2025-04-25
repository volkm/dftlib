from enum import Enum

from dftlib.exceptions.exceptions import DftInvalidArgumentException


class DftFormats(Enum):
    """
    File formats to represent DFTs.
    """

    GALILEO = 0
    JSON = 1
    SAFEST = 2
    TEXT = 3


def get_file_extension(file_format):
    """
    Get file extension for given format.
    :param file_format: DFT file format.
    :return: File extension.
    """
    if file_format == DftFormats.GALILEO:
        return ".dft"
    elif file_format == DftFormats.JSON:
        return ".json"
    elif file_format == DftFormats.SAFEST:
        return ".safest"
    elif file_format == DftFormats.TEXT:
        return ".txt"
    else:
        raise DftInvalidArgumentException("DFT format {} not known.".format(file_format))


def is_galileo_file(file):
    """
    Checks whether the given file is a DFT in the Galileo format.
    :param file: File.
    :return: True iff the file is a Galileo file.
    """
    return file.endswith(get_file_extension(DftFormats.GALILEO))


def is_json_file(file):
    """
    Checks whether the given file is a DFT in the JSON format.
    :param file: File.
    :return: True iff the file is a JSON file.
    """
    return file.endswith(get_file_extension(DftFormats.JSON))


def is_text_file(file):
    """
    Checks whether the given file is a text file which contains a DFT description.
    :param file: File.
    :return: True iff the file is a text file.
    """
    return file.endswith(get_file_extension(DftFormats.TEXT))
