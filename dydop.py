import sys, json
from powergrid import PowerGrid
from scheduler import Scheduler
import SimpleHTTPServer
import SocketServer
import subprocess
from argpareser import argparser

args = argparser()
gridJSON = json.loads(open(args['inputFile'], 'r').read())
pg = PowerGrid(gridJSON)
iterations = int(args['iterations'])

print "Number of nodes: ", len(pg.grid)
print "Root node: ", pg.root
print "Leaf nodes: ", ", ".join(pg.leaves)
print

sc = Scheduler(pg, args['stepByStep'])
for i in range(iterations):
    print
    print "iteration ",i+1,":"
    if args['stepByStep']:
        while not sc.terminated:
            raw_input()
            sc.run()
    else:
        sc.run()

    sc.reset()

sc.writeResults()
PORT = 8666

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
subprocess.call('sensible-browser "http://localhost:'+str(PORT)+'"', shell=True)
httpd.serve_forever()
