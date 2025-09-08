from enum import StrEnum
import dftlib.utility.numbers as numbers
from dftlib.exceptions.exceptions import DftTypeNotKnownException
from dftlib.storage.dft_element import DftElement, ElementType


class Distribution(StrEnum):
    EXPONENTIAL = "exponential"
    CONSTANT = "const"
    PROBABILITY = "probability"
    ERLANG = "erlang"
    WEIBULL = "weibull"
    LOGNORMAL = "lognormal"


def create_from_json(json: dict, parameters: list[str] | None = None) -> "DftBe":
    """
    Create BE from JSON string.
    :param json: JSON string.
    :param parameters: Parameters which are defined. Used for parsing parametric values.
    :return: DFT BE.
    """
    assert json["group"] == "nodes"
    # Parse data from json
    data = json["data"]
    element_id = int(data["id"])
    name = data["name"]
    assert data["type"] == "be" or data["type"] == "be_exp"
    if "position" in json:
        position = (int(json["position"]["x"]), int(json["position"]["y"]))
    else:
        position = (0, 0)

    if "distribution" in data:
        distribution = data["distribution"]
    else:
        distribution = "exponential"

    if distribution == "const" or distribution == "constant":
        failed = bool(data["failed"])
        element = BeConstant(element_id, name, failed, position)
    elif distribution == "probability":
        probability = numbers.parse_number(data["prob"], parameters)
        dorm = numbers.parse_number(data["dorm"], parameters)
        element = BeProbability(element_id, name, probability, dorm, position)
    elif distribution == "exponential":
        rate = numbers.parse_number(data["rate"], parameters)
        dorm = numbers.parse_number(data["dorm"], parameters)
        if "repair" in data:
            repair = numbers.parse_number(data["repair"], parameters)
        else:
            repair = 0.0
        element = BeExponential(element_id, name, rate, dorm, repair, position)
    elif distribution == "erlang":
        rate = numbers.parse_number(data["rate"], parameters)
        phases = int(data["phases"])
        dorm = numbers.parse_number(data["dorm"], parameters)
        element = BeErlang(element_id, name, rate, phases, dorm, position)
    elif distribution == "weibull":
        shape = numbers.parse_number(data["shape"], parameters)
        rate = numbers.parse_number(data["rate"], parameters)
        element = BeWeibull(element_id, name, shape, rate, position)
    elif distribution == "lognormal":
        mean = numbers.parse_number(data["mean"], parameters)
        stddev = numbers.parse_number(data["stddev"], parameters)
        element = BeLognormal(element_id, name, mean, stddev, position)
    else:
        raise DftTypeNotKnownException("BE distribution '{}' not known.".format(distribution))

    if "relevant" in data:
        element.relevant = bool(data["relevant"])
    return element


class DftBe(DftElement):
    """
    Basic element (BE).
    """

    def __init__(self, element_id: int, name: str, distribution: Distribution, position: tuple[float, float]) -> None:
        DftElement.__init__(self, element_id, name, ElementType.BE, position)
        self.distribution: Distribution = distribution

    def get_json(self) -> dict:
        json = DftElement.get_json(self)
        json["data"]["distribution"] = self.distribution
        return json

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, DftBe)
        return self.distribution == other.distribution


class BeConstant(DftBe):
    """
    Constant failed/failsafe BE.
    """

    def __init__(self, element_id: int, name: str, failed: bool, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.CONSTANT, position)
        self.failed = failed

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["failed"] = self.failed
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " constant, {}".format("failed" if self.failed else "failsafe")
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeConstant)
        return self.failed == other.failed

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.CONSTANT


class BeProbability(DftBe):
    """
    BE with constant probability distribution.
    """

    def __init__(self, element_id: int, name: str, probability: float | str, dorm: float | str, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.PROBABILITY, position)
        self.probability = probability
        self.dorm = dorm

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["prob"] = str(self.probability)
        json["data"]["dorm"] = str(self.dorm)
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " probability, prob {}".format(self.probability)
        if not numbers.is_one(self.dorm):
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeProbability)
        if self.probability != other.probability:
            return False
        if self.dorm != other.dorm:
            return False
        return True

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.PROBABILITY
        assert numbers.is_probability(self.probability)


class BeExponential(DftBe):
    """
    BE with exponential distribution.
    """

    def __init__(self, element_id: int, name: str, rate: float | str, dorm: float | str, repair: float | str, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.EXPONENTIAL, position)
        self.rate = rate
        self.dorm = dorm
        self.repair = repair

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["rate"] = str(self.rate)
        json["data"]["dorm"] = str(self.dorm)
        json["data"]["repair"] = str(self.repair)
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " exponential, rate {}".format(self.rate)
        if not numbers.is_zero(self.repair):
            s += ", repair {}".format(self.repair)
        if not numbers.is_one(self.dorm):
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeExponential)
        if self.rate != other.rate:
            return False
        if self.dorm != other.dorm:
            return False
        if self.repair != other.repair:
            return False
        return True

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.EXPONENTIAL
        assert numbers.is_not_negative(self.rate)
        assert numbers.is_probability(self.dorm)
        assert numbers.is_not_negative(self.repair)


class BeErlang(DftBe):
    """
    BE with Erlang distribution.
    """

    def __init__(self, element_id: int, name: str, rate: float | str, phases: int, dorm: float | str, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.ERLANG, position)
        self.rate = rate
        self.phases = phases
        self.dorm = dorm

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["rate"] = str(self.rate)
        json["data"]["phases"] = str(self.phases)
        json["data"]["dorm"] = str(self.dorm)
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " erlang, rate {}, phases {}".format(self.rate, self.phases)
        if not numbers.is_one(self.dorm):
            s += ", dormancy {}".format(self.dorm)
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeErlang)
        if self.rate != other.rate:
            return False
        if self.phases != other.phases:
            return False
        if self.dorm != other.dorm:
            return False
        return True

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.ERLANG
        assert numbers.is_not_negative(self.rate)
        assert numbers.is_probability(self.dorm)
        assert self.phases >= 1


class BeWeibull(DftBe):
    """
    BE with Weibull distribution.
    """

    def __init__(self, element_id: int, name: str, shape: float | str, rate: float | str, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.WEIBULL, position)
        self.shape = shape
        self.rate = rate

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["shape"] = str(self.shape)
        json["data"]["rate"] = str(self.rate)
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " weibull, shape {}, rate {}".format(self.shape, self.rate)
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeWeibull)
        if self.shape != other.shape:
            return False
        if self.rate != other.rate:
            return False
        return True

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.WEIBULL
        assert numbers.is_not_negative(self.rate)
        assert numbers.is_not_negative(self.shape)


class BeLognormal(DftBe):
    """
    BE with log-normal distribution.
    """

    def __init__(self, element_id: int, name: str, mean: float | str, stddev: float | str, position: tuple[float, float]) -> None:
        DftBe.__init__(self, element_id, name, Distribution.LOGNORMAL, position)
        self.mean = mean
        self.stddev = stddev

    def get_json(self) -> dict:
        json = DftBe.get_json(self)
        json["data"]["mean"] = str(self.mean)
        json["data"]["stddev"] = str(self.stddev)
        return json

    def __str__(self) -> str:
        s = super().__str__()
        s += " lognormal, mean {}, stddev {}".format(self.mean, self.stddev)
        return s

    def compare(self, other: DftElement, respect_ids: bool) -> bool:
        if not super().compare(other, respect_ids):
            return False
        assert isinstance(other, BeLognormal)
        if self.mean != other.mean:
            return False
        if self.stddev != other.stddev:
            return False
        return True

    def check_valid(self) -> None:
        assert self.element_type == ElementType.BE
        assert self.distribution == Distribution.LOGNORMAL
        assert numbers.is_not_negative(self.mean)
        assert numbers.is_not_negative(self.stddev)
