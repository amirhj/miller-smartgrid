from powergrid import PowerGrid
import json

class Scheduler:
    def __init__(self, powerGrid, stepByStep=False):
        self.pg = powerGrid
        self.stepByStep = stepByStep
        self.clock = 0
        self.terminated = False
        self.results = []

    def run(self):
        while not self.terminated:
            oneIsReady = False
            for node in self.pg.grid:
                n = self.pg.grid[node]
                if n.isReady():
                    oneIsReady = True
                    self.clock += 1
                    print
                    print "clock ",self.clock,": Node ",n.id," is running..."
                    print
                    n.run()
                    if self.isFinished():
                        return
                    if self.stepByStep:
                        return
            if not oneIsReady:
                raise Exception('Error: No node is ready to run.')

    def isFinished(self):
        for c in self.pg.leaves:
            if not self.pg.grid[c].isFinished:
                return False
        self.terminated = True
        self.saveResults()
        for n in self.pg.grid:
            self.pg.grid[n].reset()
        return True

    def reset(self):
        self.terminated = False

    def saveResults(self):
        results = { 'connections' : {} }
        for n in self.pg.grid:
            parentId = self.pg.grid[n].parent
            if parentId != None:
                results['connections'][parentId + '-' + n] = self.pg.grid[n].finalResult[0]
                results['connections'][n + '-' + parentId] = self.pg.grid[n].finalResult[0]

        results['generators'] = { g:self.pg.generators[g].value for g in self.pg.generators }

        self.results.append(results)

    def writeResults(self):
        out = open('results.txt', 'w')
        out.write(json.dumps(self.results, indent=4))
        out.close()
