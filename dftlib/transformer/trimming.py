from collections import deque

import dftlib.storage.dft_gates as dft_gates


def trim(dft):
    """
    Trim parts of the DFT which do not contribute to the top level element.
    :param dft: DFT which will be modified.
    """

    # List of possible unused elements to trim
    unused = {elem_id: element for elem_id, element in dft.elements.items()}
    visited = set()

    # Perform breadth-first search to find all necessary elements
    queue = deque()
    queue.append(dft.top_level_element)
    while len(queue) > 0:
        current = queue.popleft()
        visited.add(current)

        if current.element_id in unused:
            # Element is necessary
            del unused[current.element_id]

        # Continue search
        if current.is_be():
            # Add possible SEQ or FDEP gates
            for parent in current.ingoing:
                if isinstance(parent, dft_gates.DftDependency) or isinstance(parent, dft_gates.DftSeq) or isinstance(parent, dft_gates.DftMutex):
                    if parent not in visited:
                        queue.append(parent)
        elif current.is_gate():
            # Add children of gate
            for child in current.outgoing:
                if child not in visited:
                    queue.append(child)

    assert len(unused) == len(dft.elements) - len(visited)

    # Remove unused elements
    for element_id, element in unused.items():
        if not element.relevant:
            dft.remove(element)
