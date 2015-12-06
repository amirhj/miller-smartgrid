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

    def readMessageBox(self):
        return { m.sender: m for m in self.messageBox }

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
            messages = self.readMessageBox()
            for a in range(self.generator):
                isFirst = True
                minPowerCost = 0
                minPCState = None
                CCI = [ -1 for m in self.messageBox]
                rFlow = 0

                # making cartesian product of children's messages and choosing the one with minimum cost
                while CCI[0] < len(self.messageBox):
                    rCO = self.CI*a + sum([ self.messageBox[j][1][CCI[j]][1] for j in range(len(self.messageBox))])

                    # choosing minimum cost
                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ (self.messageBox[j][0], self.messageBox[j][1][CCI[j]]) for j in range(len(self.messageBox))])
                        rFlow = a + self.load + sum([ self.messageBox[j][1][CCI[j]][0] for j in range(len(self.messageBox))])
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
        self.finalResult = None
        if self.isRoot():
            isFirst = True
            minPowerCost = 0
            minPCState = None
            minGenerator = 0
            CCI = [ -1 for m in self.messageBox]
            rFlow = 0

            for a in range(self.generator):
                # making cartesian product of children's messages and choosing the one with minimum cost
                while CCI[0] < len(self.messageBox):
                    rCO = self.CI*a + sum([ self.messageBox[j][1][CCI[j]][1] for j in range(len(self.messageBox))])

                    # choosing minimum cost
                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ (self.messageBox[j][0], self.messageBox[j][1][CCI[j]]) for j in range(len(self.messageBox))])
                        rFlow = a + self.load + sum([ self.messageBox[j][1][CCI[j]][0] for j in range(len(self.messageBox))])
                        minGenerator = a
                        isFirst = False

                    for i in reversed(range(len(self.messageBox)):
                        if CCI[i] < len(self.messageBox[i]):
                            CCI[i] += 1
                            if CCI[i] == len(self.messageBox[i]):
                                CCi[i] = 0
                            else:
                                break

            self.finalResult = (rFlow, minPowerCost, minGenerator)
            flowCO = (rFlow, minPowerCost)
            self.OPCStates[flowCO] = minGenerator

            self.propagateValueToChildren(minPCState)
        else:
            if self.messageBox[0][0] == self.parnet:
                optimalFlowCO = self.messageBox[0]
                self.finalResult = (optimalFlowCO[0], optimalFlowCO[1], self.OPCStates[optimalFlowCO])
                if not self.isLeaf():
                    self.propagateValueToChildren(self.PCStates[optimalFlowCO])

    def propagateValueToChildren(self, messages):
        for m in messages:
            self.powerGrid.grid[m[0]].messageBox.append((self.id, m[1]))

class PowerGrid:
    def __init__(self, gridJSON):
        self.grid = {}
        self.gridJSON = gridJSON
        self.initialize(gridJSON)

    def initialize(self, gridJSON):
        children = set()
        parents = set()
        for n in gridJSON:
            parents.add(n)
            for c in gridJSON[n]['children']:
                children.add(c)

        self.root = list(parents - children)[0]
        if len(parents - children) > 0:
            raise Exception('Error: More than one root found.')

        self.leaves = list(children - parents)
        if len(children - parents) == 0:
            raise Exception('Error: Graph is not acyclic.')

        for n in gridJSON:
            # looking for parent of node n
            parent = None
            for p in gridJSON:
                if n in gridJSON[p]['children']:
                    parent = p

            node = Node(n, gridJSON[n]['load'], gridJSON[n]['generator'], gridJSON[n]['CI'], parent)
            node.setPoweGrid(self)
            self.grid[n] = node

    def getChildren(self, nodeId):
        return self.gridJSON[nodeId]['children']

    def isLeaf(self, nodeId):
        return nodeId in self.leaves

class Message:
    def __init__(self, sender, reciver, content)
        self.sender = sender
        self.reciver = reciver
        self.content = content
