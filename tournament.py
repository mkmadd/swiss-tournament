#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from binning_and_graph_construction import get_pairs

BYE = 1         # player id for bye is 1


def connect(dbname='tournament'):
    """Connect to the PostgreSQL database, returning a connection and cursor."""
    try:
        conn = psycopg2.connect("dbname={}".format(dbname))
    except psycopg2.OperationalError, e:
        print e
        return None, None
    cursor = conn.cursor()
    return conn, cursor
    
    
def clearAll():
    """Drop all tables and reset with tournament.sql"""
    conn, cursor = connect()
    cursor.execute("DROP TABLE IF EXISTS players CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS tournaments CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS tournament_players CASCADE;")
    cursor.execute("DROP TABLE IF EXISTS matches CASCADE;")
    cursor.execute(open("tournament.sql", "r").read())
    conn.commit()
    conn.close()
    

def deleteMatches():
    """Remove all match records from the database."""
    conn, cursor = connect()
    cursor.execute("DELETE FROM matches;")
    conn.commit()
    conn.close()
    


def deletePlayers():
    """Remove all the player records from the database."""
    conn, cursor = connect()
    cursor.execute("DELETE FROM players WHERE id <> 1;")
    conn.commit()
    conn.close()


def deleteTournaments():
    """Remove all tournament records from the database."""
    conn, cursor = connect()
    cursor.execute("DELETE FROM tournaments CASCADE;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn, cursor = connect()
    cursor.execute("SELECT COUNT(*) AS num FROM players WHERE id <> 1;")
    num = cursor.fetchall()
    conn.close()
    return num[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database.
    
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
    
    Args:
      name: the player's full name (need not be unique).
      
    Returns:
      int: id of the player just added
    """
    conn, cursor = connect()
    query = """INSERT INTO players (name) VALUES(%s) RETURNING id;"""
    cursor.execute(query, [name])
    id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return id


def getTournaments():
    """Retrieve a list of all tournaments in the tournament database.
    
    Returns:
      List of (id, name) tuples
        id: the tournament id
        name: the tournament name
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM tournaments;")
    tournaments = cursor.fetchall()
    conn.close()
    return tournaments

    
def getTournamentByName(name):
    """Retrieve tournament id and name given a name.
    
    If more than one exist in database, returns list of all.
    
    Returns:
      List of (id, name) tuples
        id: tournament id matching name
        name: name
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM tournaments WHERE name = %s;", [name])
    tournaments = cursor.fetchall()
    conn.close()
    return tournaments


def getTournamentById(id):
    """Retrieve tournament id and name given an id.
    
    Returns:
      (id, name) tuple
        id: tournament id matching name
        name: name
    """
    conn, cursor = connect()
    cursor.execute("SELECT * FROM tournaments WHERE id = %s;", [id])
    tournaments = cursor.fetchone()
    conn.close()
    return tournaments


def getByeId():
    """Retrieve id of player named 'bye'
    
    Returns:
      int: id used to represent a bye
    """
    conn, cursor = connect()
    cursor.execute("SELECT id FROM players WHERE name = 'bye';")
    id = cursor.fetchone()[0]
    conn.close()
    return id


class Tournament():
    """Encapsulates id, name, and methods of a tournament.
    
    A tournament is stored as just a name and an id in the tournament 
    database.  Most methods for retrieving data from the database are 
    limited to a single tournament, and this class captures those methods.
    
    Methods for associating and disassociating a player with a tournament, 
    reporting and deleting matches occurring within a tournament, reporting 
    tournament standings and determining tournament pairings are provided.
    
    Attributes:
      id: id of the tournament
      name: name of the tournament
    """
    
    def __init__(self, name, id=None):
        """Set id and name, registering a new tournament if no id given."""
        self.name = name
        if id is None:
            self._register()
        else:
            self.id = id

        
    def _register(self):
        """Adds tournament to the tournament database.
        
        The database assigns a unique serial id number for the tournament.
        id is returned and assigned to self.id
        
        Args:
          name: the tournament name (need not be unique).
        """
        conn, cursor = connect()
        query = """INSERT INTO tournaments (name) VALUES(%s) RETURNING id;"""
        cursor.execute(query, [self.name])
        self.id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        
    def deleteMatches(self):
        """Remove match records from the database.
        
           If tournament id is specified, delete all matches for that 
           tournament, else delete all matches for all tournaments.
        """
        conn, cursor = connect()
        cursor.execute("DELETE FROM matches WHERE tournament = %s;", [self.id])
        conn.commit()
        conn.close()

        
    def countPlayers(self):
        """Return the number of players currently entered in this tournament.
        
        Returns:
          int: number of players in entered in this tournament
        """
        conn, cursor = connect()
        query = """SELECT COUNT(*) AS num
                   FROM tournament_players
                   WHERE tournament = %s;
                """
        cursor.execute(query, [self.id])
        num = cursor.fetchall()
        conn.close()
        return num[0][0]


    def enterPlayer(self, player_id):
        """Enters an existing player into an existing tournament
        
        Args:
          player_id: id of the player to be added
        """
        conn, cursor = connect()
        query = """INSERT INTO tournament_players (tournament, player) 
                   VALUES(%s, %s);
                """
        cursor.execute(query, [self.id, player_id])
        conn.commit()
        conn.close()

        
    def removePlayer(self, player_id):
        """Removes a player from a tournament
        
        Args:
          player_id: id of the player to be removed
        """
        conn, cursor = connect()
        query = """DELETE FROM tournament_players
                   WHERE tournament = %s AND player = %s;
                """
        cursor.execute(query, [self.id, player_id])
        conn.commit()
        conn.close()

    def playerStandings(self):
        """Returns a list of the players and their win/draw/loss records.

        The first entry in the list should be the player in first place, 
        or a player tied for first place if there is currently a tie.  
        Players are sorted by wins, then draws, then opponent points (3 
        pts for win, 1 for draw, 0 for loss).
        
        Returns:
          A list of tuples, each of which contains (id, name, wins, draws,
          losses):
            id: the player's unique id (assigned by the database)
            name: the player's full name (as registered)
            wins: the number of matches the player has won
            draws: the number of matches the player has drawn
            losses: the number of matches the player has lost
        """
        conn, cursor = connect()
        query = """SELECT id, name, wins, draws, losses
                    FROM get_standings_from_tourn(%s)
                    LEFT JOIN get_opponent_points_from_tourn(%s)
                    USING (id)            
                    ORDER BY wins DESC, draws DESC, points DESC;
                """
        cursor.execute(query, [self.id, self.id])
        standings = cursor.fetchall()
        conn.close()
        return standings

    def reportMatch(self, winner, loser, draw=False):
        """Records the outcome of a single match between two players.

        Args:
          winner:  the id number of the player who won
          loser:  the id number of the player who lost
          draw: Whether match was a draw, default is false
        """
        conn, cursor = connect()
        query = """INSERT INTO matches (tournament, winner, loser, draw) 
                   VALUES (%s, %s, %s, %s);"""
        cursor.execute(query, [self.id, winner, loser, draw])
        conn.commit()
        conn.close()

    # A couple of helper functions
    def reportBye(self, player):
        self.reportMatch(player, BYE)

    def reportDraw(self, player1, player2):
        self.reportMatch(player1, player2, True)
     
     
    def swissPairings(self):
        """Returns a list of pairs of players for the next round of a match.
      
        Calls get_pairs() from binning_and_graph_construction.py.  This 
        function creates a graph where every player is a node and edges are 
        possible pairings, weighted according to how preferable the pairing 
        would be.  Players are divided into groups with the same win-draw-loss 
        record.  Ideal pairings match the top half of each group with the 
        bottom half - e.g. for players ranked 1, 2, 3, 4, 1 would be paired 
        with 3 and 2 with 4.  Playing non-ideal partners incurs a weight 
        penalty the farther one goes from the ideal, with an additional 
        penalty for jumping between win groups.
        
        Once the weighted graph is constructed, a max weight matching algorithm
        from the networkx package is called to determine final pairings.
        
        A chief strength of this method is that rematches do not occur.
        
        Returns:
          A list of tuples, each of which contains (id1, name1, id2, name2)
            id1: the first player's unique id
            name1: the first player's name
            id2: the second player's unique id
            name2: the second player's name
        """
        conn, cursor = connect()
        query = """SELECT * FROM get_info_for_pairing_from_tourn(%s);"""
        cursor.execute(query, [self.id])
        pairing_info = cursor.fetchall()
        conn.close()
        pairings = get_pairs(pairing_info)
        return pairings
