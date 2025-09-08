class DftTypeNotKnownException(Exception):
    """
    Exception when the type of the DFT element is not known.
    """


class DftTypeNotSupportedException(Exception):
    """
    Exception when the type of the DFT element is not supported.
    """


class DftInvalidArgumentException(Exception):
    """
    Exception when the argument in a DFT is invalid.
    """


class ToolNotFound(Exception):
    """
    Exception when the required tool was not found.
    """


class ToolError(Exception):
    """
    Exception when running the tool lead to an error.
    """
