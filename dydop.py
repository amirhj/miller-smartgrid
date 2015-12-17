import sys, json
from powergrid import PowerGrid
from scheduler import Scheduler

gridJSON = json.loads(open(sys.argv[1], 'r').read())
pg = PowerGrid(gridJSON)
iterations = int(sys.argv[2])

print "Number of nodes: ", len(pg.grid)
print "Root node: ", pg.root
print "Leaf nodes: ", ", ".join(pg.leaves)
print

sc = Scheduler(pg, len(sys.argv) > 3)
for i in range(iterations):
    print
    print "iteration ",i+1,":"
    if len(sys.argv) > 3:
        while not sc.terminated:
            raw_input()
            sc.run()
    else:
        sc.run()

    sc.reset()

sc.writeResults()
