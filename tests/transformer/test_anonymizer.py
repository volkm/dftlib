from helpers.helper import get_example_path
import dftlib.io.parser
import dftlib.transformer.anonymizer


def test_anonymize_small():
    file = get_example_path("simplify", "small.json")
    dft = dftlib.io.parser.parse_dft_json(file)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5
    assert dft.size_elements() == 5
    names = ["A", "B", "C", "D", "E"]
    for i in range(0, 5):
        assert dft.get_element(i).name == names[i]

    dftlib.transformer.anonymizer.make_anonymous(dft)
    no_be, no_static, no_dynamic, no_elements = dft.statistics()
    assert no_be == 3
    assert no_static == 2
    assert no_dynamic == 0
    assert no_elements == 5
    assert dft.size_elements() == 5
    for i in range(0, 5):
        assert dft.get_element(i).name == "A" + str(i)
