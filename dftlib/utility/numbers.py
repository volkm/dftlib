def parse_number(number, parameters):
    """
    Parse number.
    First, the number is parsed as a float. If this is not possible (and parameters are given), simply return the rational function as a string.
    :param number: Number to parse.
    :param parameters: Parameters which are defined. If none are given, the number is parsed as a float.
    :return: Number as float (default) or as string (if it cannot be handled as a float and parameters are present).
    """
    if parameters is None:
        # Parse as float
        return float(number)
    else:
        # Still try to parse as a float first
        try:
            return float(number)
        except ValueError:
            # Number is not float -> simply keep as string
            return number


def is_one(number):
    """
    Check whether a number is equal to one.
    :param number: Number represented either as float or string.
    :return: True iff number equals one.
    """
    if isinstance(number, float) or isinstance(number, int):
        return number == 1
    else:
        assert isinstance(number, str)
        return number == "1.0" or number == "1"


def is_zero(number):
    """
    Check whether a number is equal to zero.
    :param number: Number represented either as float or string.
    :return: True iff number equals zero.
    """
    if isinstance(number, float) or isinstance(number, int):
        return number == 0
    else:
        assert isinstance(number, str)
        return number == "0.0" or number == "0"
