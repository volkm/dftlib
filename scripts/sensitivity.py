#!/usr/bin/python3
import os.path
import sys
import subprocess
import re
import time
import argparse
import math

STORM_PATH = os.path.expanduser("~/develop/dft-storm/build/bin/")


class StormRunResult:
    """
    Results (and timings) of Storm run.
    """

    def __init__(self):
        self.results = []
        self.total_time = None
        self.building_time = None
        self.modelchecking_time = None


class SensitivityResult:
    def __init__(self, name):
        self.name = name
        self.properties = []

        self.comp_failed = None
        self.comp_operational = None
        self.comp_failed_sys_failed = None
        self.comp_operational_sys_failed = None
        self.sys_failed = None
        self.sys_operational = None
        self.comp_failed_sys_operational = None
        self.comp_operational_sys_operational = None
        self.comp_failed_isolation = None
        self.factor = None
        self.result_sens = None

    def property_string(self):
        return ";".join(self.properties)


def run_storm_dft(filename, arguments, quiet, storm_path):
    """
    Run Storm-dft on the given file and return the result.
    :param filename: File path.
    :param arguments: Additional cmdline arguments (e.g. properties).
    :param quiet: If True, no output is printed.
    :param storm_path: Path of Storm.
    :return: StormRunResult.
    """
    # Run storm-dft on filename and return result
    run_args = [os.path.join(storm_path, "storm-dft"), "-dft", filename]
    run_args.extend(arguments)

    output = run_tool(run_args, quiet)

    result = StormRunResult()
    # Parse result
    match = re.search(r'Result: \[(.*)\]', output)
    if match:
        result.results = match.group(1)
        result.results = result.results.split(', ')
        result.results = [float(res) for res in result.results]

    # Parse timings
    match = re.search(r'Exploration:\s*(.*)s', output)
    if match:
        result.building_time = match.group(1)
        result.building_time = float(result.building_time)

    match = re.search(r'Modelchecking:\s*(.*)s', output)
    if match:
        result.modelchecking_time = match.group(1)
        result.modelchecking_time = float(result.modelchecking_time)

    match = re.search(r'Total:\s*(.*)s', output)
    if match:
        result.total_time = match.group(1)
        result.total_time = float(result.total_time)

    return result


def run_storm(filename, arguments, quiet, storm_path):
    """
    Run Storm on the given file and return the result.
    :param filename: File path.
    :param arguments: Additional cmdline arguments (e.g. properties).
    :param quiet: If True, no output is printed.
    :param storm_path: Path of Storm.
    :return: StormRunResult.
    """
    # Run storm on filename and return result
    run_args = [os.path.join(storm_path, "storm"), "-drn", filename]
    run_args.extend(arguments)

    output = run_tool(run_args, quiet)

    run_result = StormRunResult()
    # Parse result
    regex = re.compile(r'Result \(for initial states\): (.*)')
    for match in regex.finditer(output):
        run_result.results.append(float(match.group(1)))

    # Parse timings
    match = re.search(r'Exploration:\s*(.*)s', output)
    if match:
        run_result.building_time = match.group(1)
        run_result.building_time = float(run_result.building_time)

    match = re.search(r'Modelchecking:\s*(.*)s', output)
    if match:
        run_result.modelchecking_time = match.group(1)
        run_result.modelchecking_time = float(run_result.modelchecking_time)

    Match = re.search(r'Total:\s*(.*)s', output)
    if match:
        run_result.total_time = match.group(1)
        run_result.total_time = float(run_result.total_time)

    return run_result


def run_tool(tool_arguments, quiet=False):
    """
    Executes a process,
    :returns: the `stdout`
    """
    pipe = subprocess.Popen(tool_arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = ""
    for line in iter(pipe.stdout.readline, ""):
        if not line and pipe.poll() is not None:
            break
        output = line.decode(encoding='UTF-8').rstrip()
        if output != "":
            if not quiet:
                print("\t * " + output)
            result += "\n" + output
    return result


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    if sys.version_info[0] == 3 and sys.version_info[1] >= 5:
        # Needs python >= 3.5
        return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
    else:
        # For python < 3.5
        if a == b:
            return True
        if a == float('inf'):
            return b == float('inf')
        if b == float('inf'):
            return a == float('inf')
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running sensitivity analysis with Storm-dft')
    parser.add_argument('--location', help='the path for Storm', default=STORM_PATH)
    parser.add_argument('--file', help='the example file', required=True)
    parser.add_argument('--file-isolation', help='the example file for the component in isolation (if non-individual failures are possible)', default=None)
    parser.add_argument('--value-isolation', help='the value for the component(s) in isolation (if non-individual failures are possible)', default=None)
    parser.add_argument('--args', help='additional arguments', default="")
    parser.add_argument('--comp', help='component(s) for which to compute the sensitivity', required=True)
    parser.add_argument('--timebound', help='the timebound', type=int, required=True)
    parser.add_argument('--debuglevel', type=int, default=0, help='the debug level (0=silent, 1=print calls and intermediate results, 2=print output from Storm')
    args = parser.parse_args()

    start_time = time.time()

    # Set cmdline arguments
    cli_args = []
    if args.args != "":
        add_args = args.args.split(",")
        cli_args.extend(add_args)

    results = []
    properties = []

    components = args.comp.split(",")

    # Gather properties
    for comp in components:
        result = SensitivityResult(comp)
        # Label to indentify failure of the component
        comp_label = "\"{}_failed\"".format(comp)

        # Construct properties
        # Component failed
        result.properties.append("P=? [F[{0},{0}] {1}]".format(args.timebound, comp_label))
        # Component operational
        result.properties.append("P=? [F[{0},{0}] ! {1}]".format(args.timebound, comp_label))
        # Component failed and system failed
        result.properties.append("P=? [F[{0},{0}] {1} & \"failed\"]".format(args.timebound, comp_label))
        # Component operational and system failed
        result.properties.append("P=? [F[{0},{0}] ! {1} & \"failed\"]".format(args.timebound, comp_label))

        if args.debuglevel > 0:
            print("Computing additional properties for better debugging.")

            # System failed
            result.properties.append("P=? [F[{0},{0}] \"failed\"]".format(args.timebound))
            # System operational
            result.properties.append("P=? [F[{0},{0}] ! \"failed\"]".format(args.timebound))
            # Component failed and system operational
            result.properties.append("P=? [F[{0},{0}] {1} & ! \"failed\"]".format(args.timebound, comp_label))
            # Component operational and system operational
            result.properties.append("P=? [F[{0},{0}] ! {1} & ! \"failed\"]".format(args.timebound, comp_label))
        results.append(result)
    assert len(results) == len(components)

    # Run Storm
    property_str = ";".join([res.property_string() for res in results])
    arguments = cli_args + ["--prop", property_str]
    if args.debuglevel > 0:
        print("Running '{}' with arguments '{}'".format(args.file, arguments))
    storm_result = run_storm(args.file, arguments, args.debuglevel < 2, args.location)
    if not storm_result.results:
        print("Error occurred on example '{}' with arguments '{}'".format(args.file_isolation, arguments))
        exit(1)

    if args.debuglevel > 0:
        assert len(storm_result.results) == 8 * len(results)
    else:
        assert len(storm_result.results) == 4 * len(results)

    # Get individual results
    i = 0
    for res in results:
        res.comp_failed, res.comp_operational, res.comp_failed_sys_failed, res.comp_operational_sys_failed = storm_result.results[i:i + 4]
        i += 4
        if args.debuglevel > 0:
            res.sys_failed, res.sys_operational, res.comp_failed_sys_operational, res.comp_operational_sys_operational = storm_result.results[i:i + 4]
            i += 4

    # Get timings
    time_total = storm_result.total_time
    time_building = storm_result.building_time
    time_model_checking = storm_result.modelchecking_time

    for res in results:
        # Check component failure in isolation
        if args.file_isolation is None:
            if args.value_isolation is not None:
                res.comp_failed_isolation = float(args.value_isolation)
            else:
                # Assume individual component failure
                res.comp_failed_isolation = res.comp_failed
                print("WARN: Component is assumed to have individual failure.")
        else:
            # Run Storm again
            property_str = "P=? [F[{0},{0}] \"failed\"]".format(args.timebound)
            arguments = cli_args + ["--prop", property_str]
            if args.debuglevel > 0:
                print("Running '{}' with arguments '{}'".format(args.file_isolation, arguments))
            storm_result_isolation = run_storm(args.file_isolation, arguments, args.debuglevel < 2, args.location)
            # Get result in isolation
            if storm_result_isolation is None:
                print("Error occurred on example '{}' with arguments '{}'".format(args.file_isolation, arguments))
                exit(1)
            else:
                assert len(storm_result_isolation.results) == 1
                # Get result in isolation
                res.comp_failed_isolation = storm_result_isolation.results[0]
                # Update timings
                time_total += storm_result_isolation.total_time
                time_building += storm_result_isolation.building_time
                time_model_checking += storm_result_isolation.modelchecking_time

        if not isclose(1.0, res.comp_failed + res.comp_operational, rel_tol=1e-5):
            print("Not equal 1: {}".format(res.comp_failed + res.comp_operational))

        if args.debuglevel > 0:
            if not isclose(1.0, res.sys_failed + res.sys_operational, rel_tol=1e-5):
                print("Not equal 1: {}".format(res.sys_failed + res.sys_operational))
            if not isclose(res.sys_failed, res.comp_failed_sys_failed + res.comp_operational_sys_failed, rel_tol=1e-5):
                print("Not equal: {} and {}".format(res.sys_failed, res.comp_failed_sys_failed + res.comp_operational_sys_failed))
            if not isclose(res.sys_operational, res.comp_failed_sys_operational + res.comp_operational_sys_operational, rel_tol=1e-5):
                print("Not equal: {} and {}".format(res.sys_operational, res.comp_failed_sys_operational + res.comp_operational_sys_operational))
            if not isclose(res.comp_failed, res.comp_failed_sys_failed + res.comp_failed_sys_operational, rel_tol=1e-5):
                print("Not equal: {} and {}".format(res.comp_failed, res.comp_failed_sys_failed + res.comp_failed_sys_operational))
            if not isclose(res.comp_operational, res.comp_operational_sys_failed + res.comp_operational_sys_operational, rel_tol=1e-5):
                print("Not equal: {} and {}".format(res.comp_operational, res.comp_operational_sys_failed + res.comp_operational_sys_operational))

        # Compute factor
        res.factor = res.comp_failed / res.comp_failed_isolation
        if args.debuglevel > 0:
            print("Factor:\t{:.7e}".format(res.factor))

        # Via unreliability
        first_fail = res.comp_failed_sys_failed / res.comp_failed
        second_fail = res.comp_operational_sys_failed / res.comp_operational
        inter_fail = first_fail - second_fail
        if args.debuglevel > 0:
            print("Intermediate result (via unrel.):\t{:.7e}".format(inter_fail))
        res.result_sens = res.factor * inter_fail
        print("Result for {} (via unrel.):\t{:.7e}".format(res.name, res.result_sens))

        if args.debuglevel > 0:
            # Compute via reliability as well
            first_op = res.comp_operational_sys_operational / res.comp_operational
            second_op = res.comp_failed_sys_operational / res.comp_failed
            inter_op = first_op - second_op
            if args.debuglevel > 0:
                print("Intermediate result (via rel.):\t{:.7e}".format(inter_op))
            result_op = res.factor * inter_op
            print("Result (via rel.):\t{:.7e}".format(result_op))

    # Timings
    if time_building is not None:
        print("Time Building:\t\t{:.2f}s".format(time_building))
    if time_model_checking is not None:
        print("Time Model Checking:\t{:.2f}s".format(time_model_checking))
    if time_total is not None:
        print("Time Storm (Total):\t{:.2f}s".format(time_total))
    print("Total Time:\t\t{:.2f}s".format(time.time() - start_time))
