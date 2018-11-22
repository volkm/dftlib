import subprocess


def run_tool(args, quiet=False):
    """
    Executes a process with the given arguments.
    :param args: Arguments.
    :param quiet: Flag indicating whether the output should be printed.
    :return: The 'stdout'.
    """
    pipe = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ""
    for line in iter(pipe.stdout.readline, ""):
        if not line and pipe.poll() is not None:
            break
        output = line.decode(encoding='UTF-8').rstrip()
        if output != "":
            if not quiet:
                print("\t * " + output)
            result = output
    return result
