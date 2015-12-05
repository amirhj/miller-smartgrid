class Node:
    def __init__(self, id, load, generator, CI, parent=None):
        self.load = load
        self.generator = generator
        self.parnet = parent
        self.messageBox = []
        self.powerGrid = None
        self.OPCStates = {}
        self.CI = CI

    def setPoweGrid(self, pg):
        self.powerGrid = pg

    def isRoot(self):
        if self.parent == None:
            return True
        return False

    def isLeaf(self):
        return self.powerGrid.isLeaf(self.id)

    def getChildren(self):
        return self.powerGrid.getChildren(self.id)

    def getParent(self):
        return self.powerGrid.grid[self.parent]

    def calculateValues(self):
        self.values = []

        if self.isLeaf():
            for a in range(self.generator):
                rFlow = a + self.load
                flowCO = (rFlow, a*CI)
                self.OPCStates[flowCO] = a
                self.values.append(flowCO)
        else:
            self.PCStates = {}
            for a in range(self.generator):
                isFirst = True
                minPowerCost = 0
                minPCState = None
                CCI = [ -1 for m in self.messageBox]
                rFlow = 0

                while CCI[0] < len(self.messageBox):
                    # do it
                    rCO = self.CI*a + sum([ self.messageBox[j][CCI[j]][1] for j in range(len(self.messageBox))])

                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ self.messageBox[j][CCI[j]] for j in range(len(self.messageBox))])
                        rFlow = a + self.load + sum([ self.messageBox[j][CCI[j]][0] for j in range(len(self.messageBox))])
                        isFirst = False

                    for i in reversed(range(len(self.messageBox)):
                        if CCI[i] < len(self.messageBox[i]):
                            CCI[i] += 1
                            if CCI[i] == len(self.messageBox[i]):
                                CCi[i] = 0
                            else:
                                break
                flowCO = (rFlow, minPowerCost)
                self.OPCStates[flowCO] = a
                self.values.append(flowCO)
                self.PCStates[flowCO] = minPCState

        self.sendMessageToParent()
        del self.messageBox[:]

    def sendMessageToParent(self):
        if not self.isRoot():
            self.powerGrid.grid[self.parnet].messageBox.append((self.id, self.values))

    def propagateValue(self):
        if self.isRoot():
            
        else:
