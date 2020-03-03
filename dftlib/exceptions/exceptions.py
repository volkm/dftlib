class DftTypeNotKnownException(Exception):
    """
    Exception when the type of the DFT element is not known.
    """
    pass


class DftTypeNotSupportedException(Exception):
    """
    Exception when the type of the DFT element is not supported.
    """
    pass


class DftInvalidArgumentException(Exception):
    """
    Exception when the argument in a DFT is invalid.
    """


class ToolNotFound(Exception):
    """
    Exception when the required tool was not found.
    """
