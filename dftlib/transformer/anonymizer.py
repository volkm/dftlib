from dftlib.storage.dft import Dft


def make_anonymous(dft: Dft, grid_layout: bool = False):
    """
    Remove all data which could identify the DFT.
    Id and name are increasing counter values.
    :param dft: DFT.
    :param grid_layout: Elements are ordered in a grid to remove positioning information.
    :return: Anonymous DFT.
    """
    counter = 0
    x = 0
    y = 0
    dist_x = 200
    dist_y = 200
    end_x = 10 * dist_x
    # Make all elements anonymous
    for element in dft.elements.values():
        element.element_id = counter
        element.name = "A{}".format(counter)
        if grid_layout:
            element.position = (x, y)
            x += dist_x
            if x > end_x:
                x = 0
                y += dist_y
        counter += 1
