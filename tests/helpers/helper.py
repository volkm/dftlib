import os


def get_example_path(*paths):
    return os.path.join(os.path.dirname(__file__), "..", "..", "examples", *paths)
