# miller-smartgrid
Implementation of paper, Optimal Decentralised Dispatch of Embedded Generation in the Smart Grid by Sam Miller et al. additionally with intermittent resources.

To run:
<pre>
	python dydop.py &lt;input-file.json&gt; -i &lt;number of iterations&gt; -p &lt;port to display graphical result in default browser&gt; &lt;other options&gt;

</pre>
NOTE: This program just works in debian based operating systems.

Example:
<pre>
	python dydop.py grid.json -i 12 -p 8000
</pre>
