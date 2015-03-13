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
- binning_and_graph_construction.py - code to produce the actual pairings
- tourament_test.py - code to test the code in tournament.py

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
function max_weight_matching() that implements an algorithm described by Zvi  
Galil in "Efficient Algorithms for Finding Maximum Matching in Graphs", ACM  
Computing Surveys, 1986.  His algorithm in turn is based on work done by Jack  
Edmonds in the area of finding augmenting paths and maximum weight matching.

More info on the networkx package can be found [here](http://networkx.github.io/documentation/networkx-1.9.1/reference/generated/networkx.algorithms.matching.max_weight_matching.html).

The binning_and_graph_construction.py file contains the code for figuring out  
appropriate weights between players and constructing a graph, calling  
max_weight_matching() from the networkx package on it, then transforming the  
output into the specified format.
