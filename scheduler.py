from powergrid import PowerGrid

class Scheduler:
    def __init__(self, powerGrid, stepByStep=False):
        self.pg = powerGrid
        self.stepByStep = stepByStep
        self.clock = 0
        self.terminated = False

    def run(self):
        while not self.terminated:
            oneIsReady = False
            for node in self.pg.grid:
                n = self.pg.grid[node]
                if n.isReady():
                    oneIsReady = True
                    self.clock += 1
                    print "clock ",self.clock,": Node ",n.id," is running..."
                    #print { self.pg.grid[n].id:self.pg.grid[n].state for n in self.pg.grid }
                    n.run()
                    if self.stepByStep:
                        return
            if not oneIsReady:
                raise Exception('Error: No node is ready to run.')
