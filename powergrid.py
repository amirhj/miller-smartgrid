class Node:
    def __init__(self, id, load, generator, CI, parent=None):
        self.id = id
        self.load = load
        self.generator = generator
        self.parent = parent
        self.messageBox = []
        self.powerGrid = None
        self.OPCStates = {}
        self.CI = CI
        # state are 1: Waiting for doing phase1, 2: Waiting for doing phase2
        self.state = 1

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
                flowCO = (rFlow, a*self.CI)
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
                first = messages.keys()[0]
                while MMCI[first] < len(messages[first].content):
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
                                if i != first:
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
            m = Message(self.id, self.parent, self.values)
            print "Node ",self.id," to parent ",self.parent,self.values
            self.powerGrid.grid[self.parent].messageBox.append(m)

    def propagateValues(self):
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
                first = messages.keys()[0]
                while MMCI[first] < len(messages[first].content):
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
                                if i != first:
                                    MMCI[i] = 0
                            else:
                                break

            self.finalResult = (rFlow, minPowerCost, minGenerator)
            flowCO = (rFlow, minPowerCost)
            self.OPCStates[flowCO] = minGenerator

            self.propagateValueToChildren(minPCState)
        else:
            if self.parent in messages:
                optimalFlowCO = messages[self.parent].content
                self.finalResult = (optimalFlowCO[0], optimalFlowCO[1], self.OPCStates[optimalFlowCO])
                if not self.isLeaf():
                    self.propagateValueToChildren(self.PCStates[optimalFlowCO])

    def propagateValueToChildren(self, messages):
        for m in messages:
            message = Message(self.id, m[0], m[1])
            print "Node ",self.id," to child ",m[0], m[1]
            self.powerGrid.grid[m[0]].messageBox.append(message)

    def isReady(self):
        if self.state == 1:
            if self.isLeaf():
                return True
            elif len(self.messageBox) == len(self.getChildren()):
                return True
            return False
        elif self.state == 2:
            if not self.isRoot():
                if len(self.messageBox) == 1:
                    if self.messageBox[0].sender == self.parent:
                        return True
                    else:
                        raise Exception('Error: Message from non parent in state 2.')
                elif len(self.messageBox) > 1:
                    raise Exception('Error: Invalid number of messages in state 2.')
        else:
            raise Exception('Error: Invalid state.')
        return False

    def run(self):
        if self.isReady():
            if self.state == 1:
                if self.isRoot():
                    self.propagateValues()
                    self.state = 1
                else:
                    self.calculateValues()
                    self.state = 2
            elif self.state == 2:
                self.propagateValues()
                self.state = 1

class PowerGrid:
    def __init__(self, gridJSON):
        self.grid = {}
        self.connections = {}
        self.leaves = []
        self.gridJSON = gridJSON['nodes']
        self.connectionsJSON = gridJSON['connections']
        self.initialize()

    def initialize(self):
        children = set()
        nodes = set()
        for n in self.gridJSON:
            nodes.add(n)
            if 'children' in self.gridJSON[n]:
                if len(self.gridJSON[n]['children']) == 0:
                    self.leaves.append(n)
                else:
                    for c in self.gridJSON[n]['children']:
                        children.add(c)
            else:
                self.leaves.append(n)

        self.root = list(nodes - children)[0]
        if len(nodes - children) > 1:
            raise Exception('Error: More than one root found.')

        for n in self.gridJSON:
            # looking for parent of node n
            parent = []
            for p in self.gridJSON:
                if n in self.gridJSON[p]['children']:
                    parent.append(p)

            if len(parent) > 1:
                raise Exception('Error: Graph is not acyclic.')

            if len(parent) == 1:
                parent = parent[0]
            else:
                parent = None

            node = Node(n, self.gridJSON[n]['load'], self.gridJSON[n]['generator'], self.gridJSON[n]['CI'], parent)
            node.setPoweGrid(self)
            self.grid[n] = node

        # connections thermal capacities
        for c in self.connectionsJSON:
            v1, v2 = c.split('-')
            self.connections[(v1,v2)] = self.connectionsJSON[c]
            self.connections[(v2,v1)] = self.connectionsJSON[c]

    def getChildren(self, nodeId):
        return self.gridJSON[nodeId]['children']

    def isLeaf(self, nodeId):
        return nodeId in self.leaves

class Message:
    def __init__(self, sender, reciver, content):
        self.sender = sender
        self.reciver = reciver
        self.content = content
