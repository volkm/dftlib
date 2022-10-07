def parse_number(number, parameters):
    """
    Parse number. Default is as float. If parameters are given, interpret as rational function.
    :param number: Number to parse.
    :param parameters: Parameters which are defined. If none are given, the number is parsed as a float.
    :return: Number as float (default) or as string (if parameters are present).
    """
    if parameters is None:
        # Parse as float
        return float(number)
    else:
        # Parametric number is simply kept as string
        return number
