import numpy.random as ran
import random

class Node:
    def __init__(self, id, loads, generators, powergrid, parent=None):
        self.id = id
        self.powerGrid = powergrid
        self.loads = { l:self.powerGrid.loads[l] for l in loads }
        self.generators = { g:self.powerGrid.generators[g] for g in generators }
        self.parent = parent
        self.messageBox = []
        self.OPCStates = {}
        # state are 1: Waiting for doing phase1, 2: Waiting for doing phase2
        self.state = 1
        self.isFinished = False

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
            # Cartesian Product Matrix columns indecies of Generators and Intermittent resources and their size
            CPMGI = { g:{ 'index':0, 'size':len(self.generators[g].domain()) } for g in self.generators }

            if len(CPMGI) > 0:
                # making cartesian product of generators values
                firstG = self.generators.keys()[0]
                while CPMGI[firstG]['index'] < CPMGI[firstG]['size']:
                    sum_generators_outputs = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators ])
                    sum_loads = sum(self.loads.values())
                    rFlow = sum_generators_outputs + sum_loads

                    sum_costs_generators = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] * self.generators[g].CI for g in self.generators ])
                    flowCO = (rFlow, sum_costs_generators)
                    self.OPCStates[flowCO] = { g: self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators }
                    self.values.append(flowCO)

                    for i in reversed(self.generators.keys()):
                        if CPMGI[i]['index'] < CPMGI[i]['size']:
                            CPMGI[i]['index'] += 1
                            if CPMGI[i]['index'] == CPMGI[i]['size']:
                                if i != firstG:
                                    CPMGI[i]['index'] = 0
                            else:
                                break
        else:
            # Minimum power cost state of childern for each flowCO
            self.PCStates = {}

            messages = self.readMessageBox()

            if len(self.generators) > 0:
                # Cartesian Product Matrix columns indecies of Generators and Intermittent resources and their size
                CPMGI = { g:{ 'index':0, 'size':len(self.generators[g].domain()) } for g in self.generators }

                # making cartesian product of generators values
                firstG = self.generators.keys()[0]
                while CPMGI[firstG]['index'] < CPMGI[firstG]['size']:
                    isFirst = True
                    minPowerCost = 0
                    minPCState = None
                    rFlow = 0

                    # Cartesian Product Matrix columns Indecies of Messages and their size
                    CPMMI = { m:{ 'index':0, 'size':len(messages[m].content) } for m in messages }

                    # making cartesian product of children's messages and choosing the one with minimum cost
                    firstM = messages.keys()[0]
                    while CPMMI[firstM]['index'] < CPMMI[firstM]['size']:
                        sum_costs_generators = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] * self.generators[g].CI for g in self.generators ])
                        sum_costs_children = sum([ messages[m].content[ CPMMI[m]['index'] ][1] for m in messages ])
                        rCO = sum_costs_generators + sum_costs_children

                        # choosing minimum cost
                        if isFirst or rCO < minPowerCost:
                            minPowerCost = rCO
                            minPCState = tuple([ (m, messages[m].content[ CPMMI[m]['index'] ]) for m in messages ])

                            sum_generators_outputs = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators ])
                            sum_flows_children = sum([ messages[m].content[ CPMMI[m]['index'] ][0] for m in messages ])
                            sum_loads = sum(self.loads.values())
                            rFlow = sum_generators_outputs + sum_loads + sum_flows_children

                            isFirst = False

                        for i in reversed(messages.keys()):
                            if CPMMI[i]['index'] < CPMMI[firstM]['size']:
                                CPMMI[i]['index'] += 1
                                if CPMMI[i]['index'] == CPMMI[i]['size']:
                                    if i != firstM:
                                        CPMMI[i]['index'] = 0
                                else:
                                    break

                    flowCO = (rFlow, minPowerCost)
                    self.OPCStates[flowCO] = { g: self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators }
                    self.values.append(flowCO)
                    self.PCStates[flowCO] = minPCState

                    for i in reversed(self.generators.keys()):
                        if CPMGI[i]['index'] < CPMGI[i]['size']:
                            CPMGI[i]['index'] += 1
                            if CPMGI[i]['index'] == CPMGI[i]['size']:
                                if i != firstG:
                                    CPMGI[i]['index'] = 0
                            else:
                                break
            else:
                isFirst = True
                minPowerCost = 0
                minPCState = None
                rFlow = 0

                # Cartesian Product Matrix columns Indecies of Messages and their size
                CPMMI = { m:{ 'index':0, 'size':len(messages[m].content) } for m in messages }

                # making cartesian product of children's messages and choosing the one with minimum cost
                firstM = messages.keys()[0]
                while CPMMI[firstM]['index'] < CPMMI[firstM]['size']:
                    sum_costs_children = sum([ messages[m].content[ CPMMI[m]['index'] ][1] for m in messages ])
                    rCO = sum_costs_children

                    # choosing minimum cost
                    if isFirst or rCO < minPowerCost:
                        minPowerCost = rCO
                        minPCState = tuple([ (m, messages[m].content[ CPMMI[m]['index'] ]) for m in messages ])

                        sum_flows_children = sum([ messages[m].content[ CPMMI[m]['index'] ][0] for m in messages ])
                        sum_loads = sum(self.loads.values())
                        rFlow = sum_loads + sum_flows_children

                        isFirst = False

                    for i in reversed(messages.keys()):
                        if CPMMI[i]['index'] < CPMMI[firstM]['size']:
                            CPMMI[i]['index'] += 1
                            if CPMMI[i]['index'] == CPMMI[i]['size']:
                                if i != firstM:
                                    CPMMI[i]['index'] = 0
                            else:
                                break

                flowCO = (rFlow, minPowerCost)
                self.OPCStates[flowCO] = { g: self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators }
                self.values.append(flowCO)
                self.PCStates[flowCO] = minPCState

        self.sendMessageToParent()

    def sendMessageToParent(self):
        if not self.isRoot():
            m = Message(self.id, self.parent, self.values)
            print "Node ",self.id," to parent ",self.parent,self.values," ",len(self.values)
            self.powerGrid.grid[self.parent].messageBox.append(m)

    def propagateValues(self):
        self.finalResult = None
        messages = self.readMessageBox()
        if self.isRoot():
            isFirst = True
            minPowerCost = 0
            minPCState = None
            minGenerator = 0
            rFlow = 0
            minFlow = 0

            if len(self.generators) > 0:
                # Cartesian Product Matrix columns Indecies of Generators and Intermittent resources and their size
                CPMGI = { g:{ 'index':0, 'size':len(self.generators[g].domain()) } for g in self.generators }

                # making cartesian product of generators values
                firstG = self.generators.keys()[0]
                while CPMGI[firstG]['index'] < CPMGI[firstG]['size']:
                    # Cartesian Product Matrix columns Indecies of Messages and their size
                    CPMMI = { m:{ 'index':0, 'size':len(messages[m].content) } for m in messages }

                    # making cartesian product of children's messages and choosing the one with minimum cost
                    firstM = messages.keys()[0]
                    while CPMMI[firstM]['index'] < CPMMI[firstM]['size']:
                        sum_generators_outputs = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators ])
                        sum_flows_children = sum([ messages[m].content[ CPMMI[m]['index'] ][0] for m in messages ])
                        sum_loads = sum(self.loads.values())
                        rFlow = sum_generators_outputs + sum_loads + sum_flows_children

                        # choosing minimum cost
                        if isFirst or abs(rFlow - 0) < abs(minFlow - 0):
                            minFlow = rFlow

                            sum_costs_generators = sum([ self.generators[g].domain()[ CPMGI[g]['index'] ] * self.generators[g].CI for g in self.generators ])
                            sum_costs_children = sum([ messages[m].content[ CPMMI[m]['index'] ][1] for m in messages ])
                            rCO = sum_costs_generators + sum_costs_children

                            minPowerCost = rCO
                            minPCState = tuple([ (m, messages[m].content[ CPMMI[m]['index'] ]) for m in messages ])
                            minGenerator = { g: self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators }
                            isFirst = False

                        for i in reversed(messages.keys()):
                            if CPMMI[i]['index'] < CPMMI[firstM]['size']:
                                CPMMI[i]['index'] += 1
                                if CPMMI[i]['index'] == CPMMI[i]['size']:
                                    if i != firstM:
                                        CPMMI[i]['index'] = 0
                                else:
                                    break

                    for i in reversed(self.generators.keys()):
                        if CPMGI[i]['index'] < CPMGI[i]['size']:
                            CPMGI[i]['index'] += 1
                            if CPMGI[i]['index'] == CPMGI[i]['size']:
                                if i != firstG:
                                    CPMGI[i]['index'] = 0
                            else:
                                break
            else:
                # Cartesian Product Matrix columns Indecies of Messages and their size
                CPMMI = { m:{ 'index':0, 'size':len(messages[m].content) } for m in messages }

                # making cartesian product of children's messages and choosing the one with minimum cost
                firstM = messages.keys()[0]
                while CPMMI[firstM]['index'] < CPMMI[firstM]['size']:
                    sum_flows_children = sum([ messages[m].content[ CPMMI[m]['index'] ][0] for m in messages ])
                    sum_loads = sum(self.loads.values())
                    rFlow = sum_loads + sum_flows_children

                    # choosing minimum cost
                    if isFirst or abs(rFlow - 0) < abs(minFlow - 0):
                        minFlow = rFlow

                        sum_costs_children = sum([ messages[m].content[ CPMMI[m]['index'] ][1] for m in messages ])
                        rCO = sum_costs_children

                        minPowerCost = rCO
                        minPCState = tuple([ (m, messages[m].content[ CPMMI[m]['index'] ]) for m in messages ])
                        minGenerator = { g: self.generators[g].domain()[ CPMGI[g]['index'] ] for g in self.generators }
                        isFirst = False

                    for i in reversed(messages.keys()):
                        if CPMMI[i]['index'] < CPMMI[firstM]['size']:
                            CPMMI[i]['index'] += 1
                            if CPMMI[i]['index'] == CPMMI[i]['size']:
                                if i != firstM:
                                    CPMMI[i]['index'] = 0
                            else:
                                break

            self.finalResult = (rFlow, minPowerCost, minGenerator)
            flowCO = (rFlow, minPowerCost)
            self.OPCStates[flowCO] = minGenerator

            print "Final result in root node:"
            print "rFlow: ",rFlow, ", minPowerCost: ", minPowerCost, ", minGenerator: ",minGenerator

            self.propagateValueToChildren(minPCState)

            self.saveGeneratorsStates(minGenerator)
        else:
            if self.parent in messages:
                optimalFlowCO = messages[self.parent].content
                self.finalResult = (optimalFlowCO[0], optimalFlowCO[1], self.OPCStates[optimalFlowCO])
                if not self.isLeaf():
                    self.propagateValueToChildren(self.PCStates[optimalFlowCO])

                print "Final result in node ",self.id, ":"
                print "rFlow: ",optimalFlowCO[0], ", minPowerCost: ", optimalFlowCO[1], ", minGenerator: ",self.OPCStates[optimalFlowCO]

            self.saveGeneratorsStates(self.OPCStates[optimalFlowCO])

    def propagateValueToChildren(self, messages):
        for m in messages:
            message = Message(self.id, m[0], m[1])
            print "Message from node ",self.id," to child ",m[0],': ', m[1]
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
                self.isFinished = True

    def reset(self):
        self.isFinished = False

    def saveGeneratorsStates(self, state):
        for g in state:
            self.generators[g].value = state[g]

class Generator:
    def __init__(self, id, max_out, CI):
        self.id = id
        self.max_out = max_out
        self.CI = CI
        self.values = range(self.max_out + 1)
        self.value = None

    def domain(self):
        return self.values

class IntermittentResource:
    def __init__(self, id, average_out, sigma, prob):
        self.id = id
        self.average_out = average_out
        self.sigma = sigma
        self.prob = prob
        self.CI = 0
        self.value = None

    def domain(self):
        # return [0, ran.normal(self.average_out, self.sigma)]
        r = random.random()
        if r < self.prob:
	       return [self.average_out]
        return [0]

class PowerGrid:
    def __init__(self, gridJSON):
        self.grid = {}
        self.connections = {}
        self.loads = {}
        self.generators = {}
        self.leaves = []
        self.levels = {}
        self.nodesJSON = gridJSON['nodes']
        self.loadsJSON = gridJSON['loads']
        self.generatorsJSON = gridJSON['generators']
        self.connectionsJSON = gridJSON['connections']
        self.initialize()

    def initialize(self):
        # Loads
        self.loads = self.loadsJSON

        # Generators
        for g in self.generatorsJSON:
            if 'average_out' in self.generatorsJSON[g]:
                self.generators[g] = IntermittentResource(g, self.generatorsJSON[g]['average_out'], self.generatorsJSON[g]['sigma'], self.generatorsJSON[g]['prob'])
            else:
                self.generators[g] = Generator(g, self.generatorsJSON[g]['max_out'], self.generatorsJSON[g]['CI'])

        children = set()
        nodes = set()
        for n in self.nodesJSON:
            nodes.add(n)
            if 'children' in self.nodesJSON[n]:
                if len(self.nodesJSON[n]['children']) == 0:
                    self.leaves.append(n)
                else:
                    for c in self.nodesJSON[n]['children']:
                        children.add(c)
            else:
                self.leaves.append(n)

        self.root = list(nodes - children)[0]
        if len(nodes - children) > 1:
            raise Exception('Error: More than one root found.')

        for n in self.nodesJSON:
            # looking for parent of node n
            parent = []
            for p in self.nodesJSON:
                if n in self.nodesJSON[p]['children']:
                    parent.append(p)

            if len(parent) > 1:
                raise Exception('Error: Graph is not acyclic.')

            if len(parent) == 1:
                parent = parent[0]
            else:
                parent = None

            self.grid[n] = Node(n, self.nodesJSON[n]['loads'], self.nodesJSON[n]['generators'], self, parent)

        # connections thermal capacities
        for c in self.connectionsJSON:
            v1, v2 = c.split('-')
            self.connections[(v1,v2)] = self.connectionsJSON[c]
            self.connections[(v2,v1)] = self.connectionsJSON[c]

        self.setLevels()

    def getChildren(self, nodeId):
        children = []
        if 'children' in self.nodesJSON[nodeId]:
            children = self.nodesJSON[nodeId]['children']
        return children

    def isLeaf(self, nodeId):
        return nodeId in self.leaves

    def isRoot(self, nodeId):
        return nodeId == self.root

    def setLevels(self):
        current_level_nodes = self.getChildren(self.root)
        self.levels = { g:None for g in self.grid }
        self.levels[self.root] = 0
        current_level = 1
        while len(current_level_nodes) > 0:
            children_level_nodes = []
            for p in current_level_nodes:
                self.levels[p] = current_level
                children = self.getChildren(p)
                for c in children:
                    self.levels[c] = current_level + 1
                    children_level_nodes.append(c)

            current_level += 1
            current_level_nodes = children_level_nodes

class Message:
    def __init__(self, sender, reciver, content):
        self.sender = sender
        self.reciver = reciver
        self.content = content
