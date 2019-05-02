def trim(dft):
    '''
    Trim parts of the DFT which do not contribute to the top level element.
    :param dft: DFT.
    :return: DFT without unnecessary parts.
    '''

    # List of unused elements to trim
    unused = {elem_id: element for elem_id, element in dft.elements.items()}
    visited = set()

    # Perform breadth-first search to find all necessary elements
    queue = [dft.top_level_element]
    while len(queue) > 0:
        current = queue[0]
        visited.add(current)
        queue = queue[1:]

        if current.element_id in unused:
            # Element is necessary
            del unused[current.element_id]

        # Continue search
        if current.is_be():
            # Add possible SEQ or FDEP gates
            for parent in current.ingoing:
                if parent.element_type == "fdep" or parent.element_type == "seq" or parent.element_type == "mutex" or parent.element_type == "pdep":
                    if parent not in visited:
                        queue.append(parent)
        elif current.is_gate():
            # Add children of gate
            for child in current.outgoing:
                if child not in visited:
                    queue.append(child)

    assert len(unused) == len(dft.elements) - len(visited)

    # Remove unused elements
    print("Removing {} unnecessary elements.".format(len(unused)))

    for element_id, element in unused.items():
        if not element.relevant:
            dft.remove(element)
