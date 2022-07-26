from dftlib.exceptions.exceptions import DftTypeNotKnownException
from dftlib.storage.dft_element import DftElement


def create_from_json(json):
    """
    Create BE from JSON string.
    :param json: JSON string.
    :return: DFT BE.
    """
    assert json['group'] == "nodes"
    # Parse data from json
    data = json['data']
    element_id = int(data['id'])
    name = data['name']
    assert data['type'] == "be" or data['type'] == "be_exp"
    if 'position' in json:
        position = (json['position']['x'], json['position']['y'])
    else:
        position = (0, 0)

    if 'distribution' in data:
        distribution = data['distribution']
    else:
        distribution = "exponential"

    if distribution == "const":
        failed = bool(data['failed'])
        element = BeConstant(element_id, name, failed, position)
    elif distribution == "probability":
        probability = float(data['prob'])
        dorm = float(data['dorm'])
        element = BeProbability(element_id, name, probability, dorm, position)
    elif distribution == "exponential":
        rate = float(data['rate'])
        dorm = float(data['dorm'])
        if 'repair' in data:
            repair = float(data['repair'])
        else:
            repair = 0
        element = BeExponential(element_id, name, rate, dorm, repair, position)
    elif distribution == "erlang":
        rate = float(data['rate'])
        phases = int(data['phases'])
        dorm = float(data['dorm'])
        element = BeErlang(element_id, name, rate, phases, dorm, position)
    elif distribution == "weibull":
        shape = float(data['shape'])
        rate = float(data['rate'])
        element = BeWeibull(element_id, name, shape, rate, position)
    elif distribution == "lognormal":
        mean = float(data['mean'])
        stddev = float(data['stddev'])
        element = BeLognormal(element_id, name, mean, stddev, position)
    else:
        raise DftTypeNotKnownException("BE distribution '{}' not known.".format(distribution))

    if 'relevant' in data:
        element.relevant = data['relevant']
    return element


class DftBe(DftElement):
    """
    Basic element (BE).
    """

    def __init__(self, element_id, name, distribution, position):
        DftElement.__init__(self, element_id, name, "be", position)
        self.distribution = distribution

    def get_json(self):
        json = DftElement.get_json(self)
        json['data']['distribution'] = self.distribution
        return json

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        return self.distribution == other.distribution


class BeConstant(DftBe):
    """
    Constant failed/failsafe BE.
    """

    def __init__(self, element_id, name, failed, position):
        DftBe.__init__(self, element_id, name, "const", position)
        self.failed = failed

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['failed'] = self.failed
        return json

    def __str__(self):
        s = super().__str__()
        s += " constant, {}".format("failed" if self.failed else "failsafe")
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        return self.failed == other.failed


class BeProbability(DftBe):
    """
    BE with constant probability distribution.
    """

    def __init__(self, element_id, name, probability, dorm, position):
        DftBe.__init__(self, element_id, name, "probability", position)
        self.probability = probability
        self.dorm = dorm

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['prob'] = str(self.probability)
        json['data']['dorm'] = str(self.dorm)
        return json

    def __str__(self):
        s = super().__str__()
        s += " probability, prob {}".format(self.probability)
        if self.dorm != 1:
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        if self.probability != other.probability:
            return False
        if self.dorm != other.dorm:
            return False
        return True


class BeExponential(DftBe):
    """
    BE with exponential distribution.
    """

    def __init__(self, element_id, name, rate, dorm, repair, position):
        DftBe.__init__(self, element_id, name, "exponential", position)
        assert self.is_be()
        self.rate = rate
        self.dorm = dorm
        self.repair = repair

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['rate'] = str(self.rate)
        json['data']['dorm'] = str(self.dorm)
        json['data']['repair'] = str(self.repair)
        return json

    def __str__(self):
        s = super().__str__()
        s += " exponential, rate {}".format(self.rate)
        if self.repair > 0:
            s += ", repair {}".format(self.repair)
        if self.dorm != 1:
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        if self.rate != other.rate:
            return False
        if self.dorm != other.dorm:
            return False
        if self.repair != other.repair:
            return False
        return True


class BeErlang(DftBe):
    """
    BE with Erlang distribution.
    """

    def __init__(self, element_id, name, rate, phases, dorm, position):
        DftBe.__init__(self, element_id, name, "erlang", position)
        assert self.is_be()
        self.rate = rate
        self.phases = phases
        self.dorm = dorm

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['rate'] = str(self.rate)
        json['data']['phases'] = str(self.phases)
        json['data']['dorm'] = str(self.dorm)
        return json

    def __str__(self):
        s = super().__str__()
        s += " erlang, rate {}, phases {}".format(self.rate, self.phases)
        if self.dorm != 1:
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        if self.rate != other.rate:
            return False
        if self.phases != other.phases:
            return False
        if self.dorm != other.dorm:
            return False
        return True


class BeWeibull(DftBe):
    """
    BE with Weibull distribution.
    """

    def __init__(self, element_id, name, shape, rate, position):
        DftBe.__init__(self, element_id, name, "weibull", position)
        assert self.is_be()
        self.shape = shape
        self.rate = rate

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['shape'] = str(self.shape)
        json['data']['rate'] = str(self.rate)
        return json

    def __str__(self):
        s = super().__str__()
        s += " weibull, shape {}, rate {}".format(self.shape, self.rate)
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        if self.shape != other.shape:
            return False
        if self.rate != other.rate:
            return False
        return True


class BeLognormal(DftBe):
    """
    BE with log-normal distribution.
    """

    def __init__(self, element_id, name, mean, stddev, position):
        DftBe.__init__(self, element_id, name, "lognormal", position)
        assert self.is_be()
        self.mean = mean
        self.stddev = stddev

    def get_json(self):
        json = DftBe.get_json(self)
        json['data']['mean'] = str(self.mean)
        json['data']['stddev'] = str(self.stddev)
        return json

    def __str__(self):
        s = super().__str__()
        s += " lognormal, mean {}, stddev {}".format(self.mean, self.stddev)
        return s

    def compare(self, other, respect_ids):
        if not super().compare(other, respect_ids):
            return False
        if self.mean != other.mean:
            return False
        if self.stddev != other.stddev:
            return False
        return True
