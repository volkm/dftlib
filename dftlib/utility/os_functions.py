import subprocess

from dftlib.exceptions.exceptions import ToolError


def run_tool(args, quiet=False):
    """
    Executes a process with the given arguments.
    :param args: Arguments.
    :param quiet: Flag indicating whether the output should be printed.
    :return: The 'stdout'.
    """
    try:
        proc = subprocess.check_output(args, stderr=subprocess.STDOUT)
        if not quiet:
            print("\t * " + proc)
        return proc
    except subprocess.CalledProcessError as e:
        raise ToolError("Tool encountered an error: {}".format(e))
