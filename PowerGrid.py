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
        messages = { m.sender: m for m in self.messageBox }
        del self.messageBox[:]
        return messages

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
                # Message Matrix Columns Indecies
                MMCI = { m:0 for m in messages }
                rFlow = 0

                # making cartesian product of children's messages and choosing the one with minimum cost
                while MMCI[0] < len(messages):
                    rCO = self.CI*a + sum([ messages[m].content[MMCI[m]][1] for m in messages])

                    # choosing minimum cost
                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ (m, messages[m].content[ MMCI[m] ]) for m in messages ])
                        rFlow = a + self.load + sum([ messages[m].content[ MMCI[m] ][0] for m in messages ])
                        isFirst = False

                    for i in reversed(messages.keys()):
                        if MMCI[i] < len(messages[i].content):
                            MMCI[i] += 1
                            if MMCI[i] == len(messages[i].content):
                                MMCI[i] = 0
                            else:
                                break

                flowCO = (rFlow, minPowerCost)
                self.OPCStates[flowCO] = a
                self.values.append(flowCO)
                self.PCStates[flowCO] = minPCState

        self.sendMessageToParent()

    def sendMessageToParent(self):
        if not self.isRoot():
            m = Message(self.id, self.parnet, self.values)
            self.powerGrid.grid[self.parnet].messageBox.append(m)

    def propagateValue(self):
        self.finalResult = None
        messages = self.readMessageBox()
        if self.isRoot():
            isFirst = True
            minPowerCost = 0
            minPCState = None
            minGenerator = 0
            # Message Matrix Columns Indecies
            MMCI = { m:0 for m in messages }
            rFlow = 0

            for a in range(self.generator):
                # making cartesian product of children's messages and choosing the one with minimum cost
                while MMCI[0] < len(messages):
                    rCO = self.CI*a + sum([ messages[m].content[MMCI[m]][1] for m in messages])

                    # choosing minimum cost
                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ (m, messages[m].content[ MMCI[m] ]) for m in messages ])
                        rFlow = a + self.load + sum([ messages[m].content[ MMCI[m] ][0] for m in messages ])
                        minGenerator = a
                        isFirst = False

                    for i in reversed(messages.keys()):
                        if MMCI[i] < len(messages[i].content):
                            MMCI[i] += 1
                            if MMCI[i] == len(messages[i].content):
                                MMCI[i] = 0
                            else:
                                break

            self.finalResult = (rFlow, minPowerCost, minGenerator)
            flowCO = (rFlow, minPowerCost)
            self.OPCStates[flowCO] = minGenerator

            self.propagateValueToChildren(minPCState)
        else:
            messages = self.readMessageBox()
            if self.parnet in messages:
                optimalFlowCO = messages[self.parnet].content[0]
                self.finalResult = (optimalFlowCO[0], optimalFlowCO[1], self.OPCStates[optimalFlowCO])
                if not self.isLeaf():
                    self.propagateValueToChildren(self.PCStates[optimalFlowCO])

    def propagateValueToChildren(self, messages):
        for m in messages:
            message = Message(self.id, m[0], m[1])
            self.powerGrid.grid[m[0]].messageBox.append(message)

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
