# Container for saving the changes on the dft during the simplification
class Transformation:
    # Number of elements in the DFT
    numberOfElementsDFT = 0

    # Number of BEs which where removed
    bes = 0

    # Number of static gates which where removed
    andGates = 0
    orGatesRem = 0
    orGatesAdd = 0
    votGates = 0

    # Number of dynamic gates which where removed
    pandGates = 0
    porGates = 0
    fdepsRem = 0
    fdepsAdd = 0
    pdeps = 0
    spares = 0
    seqs = 0

    # Init with the number of elements in the dft
    def setNumberOfElements(self, number):
        self.numberOfElementsDFT = number

    def getNumberOfElements(self):
        return self.numberOfElementsDFT

    # Functions to get number of removed elements
    def sumBEs(self):
        return self.bes

    def sumStatic(self):
        return (self.andGates + self.orGatesRem + self.votGates)

    def sumDynamic(self):
        return (self.pandGates + self.porGates + self.fdepsRem + self.pdeps + self.spares + self.seqs)

    def sumAll(self):
        return (self.sumBEs + self.sumDynamic + self.sumStatic)

    def getPercentage(self, newNumber):
        if self.numberOfElementsDFT > newNumber:
            return 100 - ((newNumber / self.numberOfElementsDFT) * 100)
        elif self.numberOfElementsDFT == newNumber:
            return 0
        else:
            return ((newNumber / self.numberOfElementsDFT) * 100) - 100

    # Functions for each type
    def getBes(self):
        return self.bes

    def addBe(self):
        self.bes = self.bes + 1

    def getAnds(self):
        return self.andGates

    def addAnd(self):
        self.andGates = self.andGates + 1

    def getOrsRem(self):
        return self.orGatesRem

    def addOrRem(self):
        self.orGatesRem = self.orGatesRem + 1

    def getOrsAdd(self):
        return self.orGatesAdd

    def addOrAdd(self):
        self.orGatesAdd = self.orGatesAdd + 1

    def getVots(self):
        return self.votGates

    def addVot(self):
        self.votGates = self.votGates + 1

    def getPands(self):
        return self.pandGates

    def addPand(self):
        self.pandGates = self.pandGates + 1

    def getPors(self):
        return self.porGates

    def addPor(self):
        self.porGates = self.porGates + 1

    def getFdepsRem(self):
        return self.fdepsRem

    def addFdepRem(self):
        self.fdepsRem = self.fdepsRem + 1

    def getFdepsAdd(self):
        return self.fdepsAdd

    def addFdepAdd(self):
        self.fdepsAdd = self.fdepsAdd + 1

    def getPdeps(self):
        return self.pdeps

    def addPdep(self):
        self.pdeps = self.pdeps + 1

    def getSpares(self):
        return self.spares

    def addSpare(self):
        self.spares = self.spares + 1

    def getSeqs(self):
        return self.seqs

    def addSeq(self):
        self.seqs = self.seqs + 1

    # Reset all
    def clear(self):
        self.bes = 0
        self.andGates = 0
        self.orGatesAdd = 0
        self.orGatesRem = 0
        self.votGates = 0
        self.pandGates = 0
        self.porGates = 0
        self.fdepsRem = 0
        self.fdepsAdd = 0
        self.pdeps = 0
        self.spares = 0
        self.seqs = 0

        self.numberOfElementsDFT = 0
