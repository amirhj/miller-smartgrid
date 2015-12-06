import sys, json
from powergrid import PowerGrid
from scheduler import Scheduler

gridJSON = json.loads(open(sys.argv[1], 'r').read())
pg = PowerGrid(gridJSON)

print "Number of nodes: ", len(pg.grid)
print "Root node: ", pg.root
print "Leaf nodes: ", ", ".join(pg.leaves)

sc = Scheduler(pg, len(sys.argv) > 2)
if len(sys.argv) > 2:
    while True:
        raw_input()
        sc.run()
else:
    sc.run()
