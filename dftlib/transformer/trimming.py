from collections import deque

import dftlib.storage.dft_gates as dft_gates

def get_releated_parents(current, visited, related_parents_visited):
    related_parents = []
    
    if isinstance(current, dft_gates.DftDependency) or isinstance(current, dft_gates.DftSeq) or isinstance(current, dft_gates.DftMutex) or isinstance(current, dft_gates.DftSpare):
        if current.element_id not in visited:
            related_parents.append(current)
    if current not in related_parents_visited:
        related_parents_visited.append(current)
        for parent in current.parents():
            if (isinstance(parent, dft_gates.DftDependency) or isinstance(parent, dft_gates.DftSeq) or isinstance(parent, dft_gates.DftMutex) or isinstance(parent, dft_gates.DftSpare) ) and parent.children()[0] == current:
                continue
            related_parents += get_releated_parents(parent, visited, related_parents_visited)
        
    return related_parents

def trim(dft):
    """
    Trim parts of the DFT in place which do not contribute to the top level element.
    :param dft: DFT which will be modified.
    :return: True iff elements were trimmed.
    """

    # List of possible unused elements to trim
    unused = {elem_id: element for elem_id, element in dft.elements.items()}
    visited = set()

    # Perform breadth-first search to find all necessary elements
    queue = deque()
    queue.append(dft.top_level_element)
    visited.add(dft.top_level_element.element_id)
    while len(queue) > 0:
        current = queue.popleft()

        if current.element_id in unused:
            # Element is necessary
            del unused[current.element_id]

        related_parents = get_releated_parents(current, visited, [])
        for related_parent in related_parents:
            if related_parent.element_id not in visited:
                queue.append(related_parent)
                visited.add(related_parent.element_id)
        
        if current.is_gate():
            # Add children of gate
            for child in current.children():
                if child.element_id not in visited:
                    queue.append(child)
                    visited.add(child.element_id)

    assert len(unused) == len(dft.elements) - len(visited)

    # Remove unused elements
    trimmed = False
    for element in unused.values():
        if not element.relevant:
            dft.remove(element)
            trimmed = True
    return trimmed


def isolated(dft):
    """
    Trim parts of the DFT in place which do not contribute to the top level element.
    :param dft: DFT which will be modified.
    :return: True iff elements were trimmed.
    """

    # List of possible unused elements to trim
    unused = {elem_id: element for elem_id, element in dft.elements.items()}
    visited = set()

    # Perform breadth-first search to find all necessary elements
    queue = deque()
    queue.append(dft.top_level_element)
    visited.add(dft.top_level_element.element_id)
    while len(queue) > 0:
        current = queue.popleft()

        if current.element_id in unused:
            # Element is necessary
            del unused[current.element_id]
        
        if current != dft.top_level_element:
            related_parents = get_releated_parents(current, visited, [])
            for related_parent in related_parents:
                if related_parent.element_id not in visited:
                    queue.append(related_parent)
                    visited.add(related_parent.element_id)
        
        if current.is_gate():
            # Add children of gate
            for child in current.children():
                if child.element_id not in visited:
                    queue.append(child)
                    visited.add(child.element_id)

    assert len(unused) == len(dft.elements) - len(visited)

    # Remove unused elements
    trimmed = False
    for element in unused.values():
        if not element.relevant:
            dft.remove(element)
            trimmed = True
    return trimmed
