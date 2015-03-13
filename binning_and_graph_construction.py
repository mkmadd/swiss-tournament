# -*- coding: utf-8 -*-
"""
A function, get_pairs(player_info), to determine the best pairings given a
list of players in a tournament.

Given each player's id, name, record, and who they've played against, this
function will determine ideal pairings with no rematches.  It can handle
draws as well as byes (for odd number of players).

Ideal matches pair top of each (win, draw, loss) group against the bottom.
E.g. if four players all have a (1, 0, 1) record, the ideal matches 1 vs 3
and 2 vs 4.

Ideal matches have a weight of 0.  For each position away from the ideal
match within the group, the weight decreases by 1.  So for the above example,
player 1 cannot be paired with themselves, and a pair of 1 vs 2 or 4 has a
weight of -1 compared to the weight of 0 for 1 vs 3.

Weight decreases by an amount equal to twice the size of the largest (w, d, l)
category for each pair outside the player's (w, d, l) category.  E.g. if 
players 5, 6, 7, and 8 were in category (0, 1, 1), and assuming no more than 
four players in any category, then player one's weight for pairing with each 
would be -4*2, - position: 1 vs 5 would be -8, 1 vs 6 would be -9, 1 vs 8
would be -11, etc.

1 vs 9, in yet another category down, would be weighted -16.


The max weight matching method from the networkx package determines the
pairing that gives the maximum weight.  It implements a Galil algorithm for
finding maximum matching in graphs (“Efficient Algorithms for Finding Maximum 
Matching in Graphs”, Zvi Galil, ACM Computing Surveys, 1986.)

From http://networkx.github.io/documentation/networkx-1.9.1/reference/
generated/networkx.algorithms.matching.max_weight_matching.html
"This method is based on the “blossom” method for finding augmenting paths 
and the “primal-dual” method for finding a matching of maximum weight, 
both methods invented by Jack Edmonds"


The idea for using maximum weight matching came from the Leaguevine blog:
https://www.leaguevine.com/blog/18/
swiss-tournament-scheduling-leaguevines-new-algorithm/

get_pairs(player_info) arguments and return:
    Args:
      player_info: list of tuples of form (id, name, wins, draws, losses,
        [opponents], opp_pts)
        id (int): player id
        name (str): player name
        wins (long): number of wins player has
        draws (long): number of draws player has
        losses (long): number of losses player has
        opponents (int[]): list of opponent ids player has already played
        opp_pts (long): number of total points opponents have (3 win, 1 draw)
        
    Returns:
      List of tuples of form (id1, name1, id2, name2) giving match pairs
      
Created on Sat Feb 28 22:13:15 2015

@author: Michael K. Maddeford
"""

from collections import OrderedDict
from networkx import Graph
from networkx.algorithms.matching import max_weight_matching

BYE = 1         # player id for bye is 1


class Player():
    def __init__(self, id, name, record, played, opp_pts):
        self.id = id
        self.name = name
        self.record = record
        self.played = played
        self.had_bye = BYE in played
        self.opp_pts = opp_pts


# Construct a dictionary of player object.  Primary reason is to retrieve
# player names once the graph algorithms has paired ids
def create_player_dict(player_info):
    player_dict = OrderedDict()
    for player in player_info:
        id = player[0]
        name = player[1]
        wins = player[2]
        draws = player[3]
        losses = player[4]
        opponents = player[5]
        opp_pts = player[6]
        new_player = Player(id, name, (wins, draws, losses), 
                            opponents, opp_pts)
        player_dict[id] = new_player
    return player_dict
        

# Construct a dictionary of (wins, draws, losses) : players
# Needed for weighting within and between (w, d, l) groups
def construct_bins(player_dict):
    binned = OrderedDict()
    had_byes = []       # keep track of players who have had byes already
    
    # Build the dictionary
    for id, player in player_dict.items():
        if player.had_bye:
            had_byes.append(id)      # add player to had_byes if had
        if player.record in binned:
            binned[player.record].append(player)
        else:
            binned[player.record] = [player]
    binned['bye'] = []
    
    # Rearrange it so even number of players in each bin.  If uneven number,
    # remove last and insert it into beginning of next bin
    for i, key in enumerate(binned):
        if len(binned[key]) % 2 != 0:
            if key != 'bye':
                next_bin = binned.items()[i+1][1]
                next_bin.insert(0, binned[key].pop())
            else:
                # if uneven number at the end, add a bye
                binned[key].append(Player(BYE, 'Bye', 
                                        (0,0,len(had_byes)), had_byes, 0))
    
    # Then if any empty bins, get rid of them
    for key in binned:
        if len(binned[key]) == 0:
            del binned[key]
            
    return binned


# Return list of pairings matching even and odd players.  For when no matches
# played yet
def simple_pairing(player_info):
    pairings = []

    # Find out if there's an odd number of players and a bye is needed
    num_players = len(player_info)

    if num_players % 2 != 0:
        player_info.append((BYE, 'bye', 0, 0, 0, [], 0))
        num_players += 1

    # Then simply pair evens with odds and call it a day
    for i in range(0, num_players, 2):
        id1 = player_info[i][0]
        name1 = player_info[i][1]
        id2 = player_info[i+1][0]
        name2 = player_info[i+1][1]
        
        pairings.append((id1, name1, id2, name2))
        
    return pairings


# Create list of tuples (player1, player 2, weight) which will be used to 
# construct a graph of player nodes with weighted edges.  Weights are 
# determined by relative position within bin and between bins
def get_weighted_edges(bins):
    weighted_edges = []
    
    # Weight penalty for moving between bins - make twice the distance of max
    # bin
    bin_weight = max(len(bins[x]) for x in bins) * 2
    
    # For each player, make an edge between player's node and each subsequent 
    # eligible player's node, with appropriate weight
    bin_lists = bins.values()       # List of all win group lists
    for i, group in enumerate(bin_lists):  # For each group of players in a bin
        for j, player in enumerate(group): # For each player in that group...
            # Pair that player with every other player not yet paired with
            for k in range(i, len(bin_lists)):
                if k == i:                  # if same bin, start at next player
                    start = j+1
                else:
                    start = 0               # else start at first player in bin
                for l in range(start, len(group)):
                    opponent = bin_lists[k][l]
                    # if opponent not already played
                    if not (opponent.id in player.played or \
                        (opponent.id == BYE and player.had_bye)):
                        # if in same bin, weight preferred opponent as 0 and
                        # increase weight by one for every spot you move away
                        # e.g. for eight teams in a win group, ideal is for 
                        # top half to pair against bottom half, 1 vs 5, 
                        # 2 vs 6, etc.  5 is 1's preferred opponent and gets 
                        # weight 0, 4 and 6 get weight 1, 3 and 7 weight 2, 
                        # and 2 and 8 weight 3
                        if i == k:
                            preferred_match = (j + len(group)/2) % len(group) 
                            # weights are negative so lower are picked by 
                            # max_weight_matching algorithm
                            weight = -abs(j - preferred_match)
                        else:
                            # if in a different bin, weight by distance from
                            # player and add bin_weight per bin distance
                            weight = -(bin_weight * (k-i) + l)
                        weighted_edges.append((player.id, opponent.id, weight))
                    # else if opponent is 'bye' and haven't had a bye yet,
                    # player is eligible for a bye
                    elif opponent.id == BYE and not player.had_bye:
                        weight = -(bin_weight * (k-i) + l)
                        weighted_edges.append((player.id, opponent.id, weight))
    
    return weighted_edges


def get_pairs(player_info):
    """Return optimal pairings given list of player standings

    Args:
      player_info: list of tuples of form (id, name, wins, draws, losses,
        [opponents], opp_pts)
        id (int): player id
        name (str): player name
        wins (long): number of wins player has
        draws (long): number of draws player has
        losses (long): number of losses player has
        opponents (int[]): list of opponent ids player has already played
        opp_pts (long): number of total points opponents have (3 win, 1 draw)
          (not used)
        
    Returns:
      List of tuples of form (id1, name1, id2, name2) giving match pairs
    """
    
    # First check if any matches have been played.  If not, just pair evens
    # with odds
    num_matches = player_info[0][2] + player_info[0][3] + player_info[0][4]
    if num_matches == 0:
        return simple_pairing(player_info)
    
    # Input players into player dict and create bins
    players = create_player_dict(player_info)
    bins = construct_bins(players)
    
    weighted_edges = get_weighted_edges(bins)   # Figure out edge weights
    
    G = Graph()                                 # Construct graph
    G.add_weighted_edges_from(weighted_edges)   # using weighted edges
    
    # Determine matches using max weight matching algorithm
    # maxcardinality = True to ensure every player is paired
    matches = max_weight_matching(G, maxcardinality=True)
    
    # Turn from dictionary of player:opponent key:value pairs to list of
    # (id1, name1, id2, name2) tuples
    pairings = []
    paired = []             # Don't want to duplicate, so keep track of pairs
    for k, v in matches.items():
        if k in paired or v in paired:
            continue
        if k != BYE and v != BYE:
            pairings.append((k, players[k].name, v, players[v].name))
        elif k == BYE:
            pairings.append((v, players[v].name, BYE, 'bye'))
        elif v == BYE:
            pairings.append((k, players[k].name, BYE, 'bye'))
        paired.append(k)
        paired.append(v)
    
    return pairings
