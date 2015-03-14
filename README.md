Tournament Results Project
==========================
Udacity Fullstack Nanodegree Project 2
--------------------------------------

This project sets up a PostgreSQL database to store the match data for a  
Swiss-style tournament.


### Base Project

The base project was simply to write a database schema to store players and  
match results, then write Python code to connect to the database, delete  
players and matches, count and register players, get player standings, store  
match results, and generate Swiss pairings.

The code to realize this is under the /basic directory.  It pairs players by  
ranking them by order of wins in the database and returning a pairing of even  
players vs odd players - a simple adjacent, or "King of the Hill", pairing.


### Extended Project

Several stretch goals were given:

- to allow more than one tournament
- to handle an odd number of players via byes
- to allow draws
- to rank players within win groups by the number of points their  
opponents have

These were all implemented.  The code is organized as follows:

- tournament.sql - the database schema
- tournament.py - implements functions to allow users to interface with the  
database and get pairings
- binning\_and\_graph\_construction.py - code to produce the actual pairings
- tournament\_test.py - code to test the code in tournament.py

For the most part, sorting and aggregation is handled in the database.  The  
exception is for the pairing.  Two issues made it far more complex to handle  
in the database, as was done in the base project.

First, instead of adjacent pairing, slide (or cross) pairing was used, where  
the strongest in each group are paired against the weakest in the group.  
Instead of simply ordering by wins and then pairing everyone with the next  
person down, I needed to know how many people were in each group, and I needed  
to handle odd numbers of people in a group.

Second, I wanted to handle the issue of rematches.  By modelling each player  
as a vertex and a possible match as an edge between vertices, I hoped to be  
able to come up with an algorithm to connect all nodes, including all and not  
visiting any more than once - a classic Hamiltonian path.  While that was a  
viable model, reducing the problem to one known to be NP-complete was not  
terribly useful.

Some searching turned up [this helpful post](https://www.leaguevine.com/blog/18/swiss-tournament-scheduling-leaguevines-new-algorithm/) on Leaguevine's blog, which  
pointed me in the right direction.  In the networkx python package, there is a  
function max\_weight\_matching() that implements an algorithm described by Zvi  
Galil in "Efficient Algorithms for Finding Maximum Matching in Graphs", ACM  
Computing Surveys, 1986.  His algorithm in turn is based on work done by Jack  
Edmonds in the area of finding augmenting paths and maximum weight matching.  
Max weight matching can be used to find the optimum (highest weight) set of  
pairings in a graph and is ideal for this problem.

More info on the networkx package can be found [here](http://networkx.github.io/documentation/networkx-1.9.1/reference/generated/networkx.algorithms.matching.max_weight_matching.html).

The binning\_and\_graph\_construction.py file contains the code for figuring out  
appropriate weights between players and constructing a graph, calling  
max\_weight\_matching() from the networkx package on it, then transforming the  
output into the specified format.

### How to Run This Program

To simply run the test program and verify all test functions pass:  

	$ python tournament_test.py


Here is an example of how to use the functions of tournament.py in your own  
program (assumes a database named tournament is setup beforehand and  
\i tournament.sql run):

	from tournament import *

	# Register a tournament
    t = Tournament("The Drones Club Annual Darts Tournament")
	
    # Register some players, capturing their database ids
    p1 = registerPlayer("Rupert Psmith")
    p2 = registerPlayer("Barmy Fotheringay-Phipps")
    p3 = registerPlayer("Bertram Wilberforce Wooster")
    p4 = registerPlayer("Oofy Prosser")
	p5 = registerPlayer("Catsmeat Potter-Pirbright")
	
	# Enter players into the tournament
    t.enterPlayer(p1)
    t.enterPlayer(p2)
    t.enterPlayer(p3)
    t.enterPlayer(p4)
    t.enterPlayer(p5)
	
	# Count tournament players
	print t.countPlayers()
	
	# Output: 5
	
	# Get initial pairings
	for pairing in t.swissPairings():
		print pairing
	
	# Output:
	# (2, 'Rupert Psmith', 3, 'Barmy Fotheringay-Phipps')
	# (4, 'Bertram Wilberforce Wooster', 5, 'Oofy Prosser')
	# (6, 'Catsmeat Potter-Pirbright', 1, 'bye')
	
	# After matches have played, store the outcomes:
	t.reportMatch(2, 3)		# Psmith beats Barmy
	t.reportMatch(5, 4)		# Oofy beats Bertie
	t.reportBye(6)			# Catsmeat gets a bye
	
	# Print out current player standings:
	print t.printStandings()
	
	# Output: [(6, 'Catsmeat Potter-Pirbright', 1L, 0L, 0L), 
	# (2, 'Rupert Psmith', 1L, 0L, 0L), (5, 'Oofy Prosser', 1L, 0L, 0L), 
	# (3, 'Barmy Fotheringay-Phipps', 0L, 0L, 1L), 
	# (4, 'Bertram Wilberforce Wooster', 0L, 0L, 1L)]
	
	# Get pairings for the next match
	for pairing in t.swissPairings():
		print pairing
	
	# Output:
	# (4, 'Bertram Wilberforce Wooster', 1, 'bye')
	# (2, 'Rupert Psmith', 6, 'Catsmeat Potter-Pirbright')
	# (3, 'Barmy Fotheringay-Phipps', 5, 'Oofy Prosser')
	
	# After matches have played, store the outcomes:
	t.reportBye(4)			# Bertie gets a bye
	t.reportMatch(2, 6)		# Psmith beats Catsmeat
	t.reportDraw(3, 5)		# Barmy ties with Oofy
	
	# Print out latest standings:
	print t.playerStandings()
	
	# Output:
	# [(2, 'Rupert Psmith', 2L, 0L, 0L), (5, 'Oofy Prosser', 1L, 1L, 0L), 
	# (6, 'Catsmeat Potter-Pirbright', 1L, 0L, 1L), 
	# (4, 'Bertram Wilberforce Wooster', 1L, 0L, 1L), 
	# (3, 'Barmy Fotheringay-Phipps', 0L, 1L, 1L)]
	
	# Remove all tournaments and players from the database
	clearAll()
