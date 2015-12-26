# miller-smartgrid
Implementation of paper, Optimal Decentralised Dispatch of Embedded Generation in the Smart Grid by Sam Miller et al. additionally with intermittent resources.

To run:
<pre>
	python dydop.py <input-file.json> -i <number of iterations> -p <port to display graphical result in default browser> <other options>

</pre>
NOTE: This program just works in debian based operating systems.

Example:
<pre>
	python dydop.py grid.json -i 12 -p 8000
</pre>
