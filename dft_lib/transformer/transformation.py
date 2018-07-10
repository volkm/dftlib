# Container for saving the changes on the dft during the simplification
class Transformation:

	# Number of elements in the DFT
	numberOfElementsDFT = 0

    # Number of BEs which where removed
    bes = 0

    # Number of static gates which where removed
    andGates = 0
    orGates = 0
    votGates = 0

    # Number of dynamic gates which where removed
    pandGates = 0
    porGates = 0
    fdeps = 0
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
        return self.andGates + self.orGates + self.votGates

    def sumDynamic(self):
        return self.pandGates + self.porGates + self.fdeps + self.pdeps + self.spares + self.eqs

    def sumAll(self):
    	return self.sumBEs + self.sumDynamic + self.sumStatic

    def getPercentage(self):
    	return (self.sumAll / self.numberOfElementsDFT) * 100

    # Functions for each type
    def getBes(self):
    	return self.bes

    def addBe(self):
    	self.bes = self.bes + 1

    def getAnds(self):
    	return self.andGates

    def addAnd(self):
    	self.andGates = self.andGates + 1

    def getOrs(self):
    	return self.orGates

    def addOr(self):
    	self.orGates = self.orGates + 1

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

    def getFdeps(self):
    	return self.fdeps

    def addFdep(self):
    	self.fdeps = self.fdeps + 1

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
	    self.orGates = 0
	    self.votGates = 0
	    self.pandGates = 0
	    self.porGates = 0
	    self.fdeps = 0
	    self.pdeps = 0
	    self.spares = 0
	    self.seqs = 0

	    self.numberOfElementsDFT = 0