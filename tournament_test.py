#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *

BYE = 1             # player id for bye is 1

def testDeleteMatches():
    deleteMatches()
    print "1. Old matches can be deleted."


def testDelete():
    deleteMatches()
    deletePlayers()
    print "2. Player records can be deleted."


def testCount():
    clearAll()
    c = countPlayers()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "3. After deleting, countPlayers() returns zero."


def testRegister():
    clearAll()
    p1 = registerPlayer("Chandra Nalaar")
    p2 = registerPlayer("Michael Maddeford")
    t1 = Tournament("Grand Smash 2015")
    t2 = Tournament("Wonderful Wars 2014")
    t1.enterPlayer(p1)
    t2.enterPlayer(p1)
    t2.enterPlayer(p2)
    c = countPlayers()
    if c != 2:
        raise ValueError(
            "After two players register, countPlayers() should be 2.")
    c = t1.countPlayers()
    if c != 1:
        raise ValueError(
            "t1.countPlayers() should return 1.")
    c = t2.countPlayers()
    if c != 2:
        raise ValueError(
            "t2.countPlayers(2) should return 2.")
    print "4. After registering two players, countPlayers() returns 2."


def testRegisterCountDelete():
    clearAll()
    # Register some players, saving their ids
    p1 = registerPlayer("Markov Chaney")
    p2 = registerPlayer("Joe Malik")
    p3 = registerPlayer("Mao Tsu-hsi")
    p4 = registerPlayer("Atlanta Hope")
    t1 = Tournament("Grand Smash 2015")
    t2 = Tournament("Wonderful Wars 2014")
    t1.enterPlayer(p1)
    t2.enterPlayer(p1)
    t2.enterPlayer(p2)
    t2.enterPlayer(p3)
    t2.enterPlayer(p4)
    c = countPlayers()
    if c != 4:
        raise ValueError(
            "After registering four players, countPlayers should be 4.")
    c = t2.countPlayers()
    if c != 4:
        raise ValueError(
            "After entering four players into tournament,"
            " t2.countPlayers should be 4.")
    t2.removePlayer(p1)
    t2.removePlayer(p3)
    c = t2.countPlayers()
    if c != 2:
        raise ValueError(
            "After removing two of four players in tournament,"
            " t2.countPlayers should be 2.")
    deletePlayers()
    c = countPlayers()
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "5. Players can be registered and deleted."


def testStandingsBeforeMatches():
    clearAll()
    # Register 5 players, saving their ids
    p1 = registerPlayer("Melpomene Murray")
    p2 = registerPlayer("Randy Schwartz")
    p3 = registerPlayer("Joe Malik")
    p4 = registerPlayer("Mao Tsu-hsi")
    p5 = registerPlayer("Atlanta Hope")
    t1 = Tournament("WSOP 2010")
    t2 = Tournament("WSOP 2011")
    # Add players and a match into a different tournament to make sure matches
    # don't show up across tournaments
    t1.enterPlayer(p1)
    t1.enterPlayer(p2)
    t1.reportMatch(p1, p2)
    # Then register 5 players into the tournament of interest
    t2.enterPlayer(p1)
    t2.enterPlayer(p2)
    t2.enterPlayer(p3)
    t2.enterPlayer(p4)
    t2.enterPlayer(p5)
    standings = t2.playerStandings()
    if len(standings) < 5:
        raise ValueError("Players should appear in playerStandings even before "
                        "they have played any matches.")
    elif len(standings) > 5:
        raise ValueError("Only registered players should appear in standings.")
    if len(standings[0]) != 5:
        raise ValueError("Each playerStandings row should have five columns.")
    for standing in standings:
        (id, name, wins, draws, losses) = standing
        if draws != 0 or wins != 0 or losses != 0:
            raise ValueError("Newly registered players should "
                             "have no wins, draws, or losses.")
        if name not in ["Melpomene Murray", "Randy Schwartz", "Joe Malik",
                        "Mao Tsu-hsi", "Atlanta Hope"]:
            raise ValueError("Registered players' names should appear in "
                             "standings, even if they have no matches played.")
    print "6. Newly registered players appear in the standings with no matches."


def testReportMatches():
    clearAll()
    # Register 5 players, saving their ids
    p1 = registerPlayer("Bruno Walton")
    p2 = registerPlayer("Boots O'Neal")
    p3 = registerPlayer("Cathy Burton")
    p4 = registerPlayer("Diane Grant")
    p5 = registerPlayer("Atlanta Hope")
    t1 = Tournament("WSOP 2010")
    t2 = Tournament("WSOP 2011")
    # Add players and a match into a different tournament to make sure matches
    # don't show up across tournaments
    t1.enterPlayer(p1)
    t1.enterPlayer(p2)
    t1.reportMatch(p2, p1)
    # Then register 5 players into the tournament of interest
    t2.enterPlayer(p1)
    t2.enterPlayer(p2)
    t2.enterPlayer(p3)
    t2.enterPlayer(p4)
    t2.enterPlayer(p5)
    t2.reportMatch(p1, p2)
    t2.reportMatch(p4, p3)
    t2.reportBye(p5)
    t2.reportMatch(p4, p1)
    t2.reportDraw(p2, p5)
    t2.reportBye(p3)
    standings = t2.playerStandings()
    for (i, n, w, d, l) in standings:
        if (w + d + l) != 2:
            raise ValueError("Each player should have two matches recorded.")
        if i in [p4] and w != 2 and d != 0 and l != 0:
            raise ValueError("Diane should have 2 wins, 0 draws, "
                             "0 losses recorded.")
        if i in [p5] and w != 1 and d != 1 and l != 0:
            raise ValueError("Atlanta should have 1 win, 1 draw, "
                             "0 losses recorded.")
        if i in [p1, p3] and w != 1 and d != 0 and l != 1:
            raise ValueError("Bruno and Cathy should have 1 win, 0 draws, "
                             "1 loss recorded.")
        if i in [p2] and w != 0 and d != 0 and l != 2:
            raise ValueError("Boots should have 0 wins, 0 draws, "
                             "2 losses recorded.")
    print "7. After a match, players have updated standings."


def testEmptyPairings():
    clearAll()
    # Register 5 players, saving their ids
    p1 = registerPlayer("Twilight Sparkle")
    p2 = registerPlayer("Fluttershy")
    p3 = registerPlayer("Applejack")
    p4 = registerPlayer("Pinkie Pie")
    p5 = registerPlayer("Darth Vader")
    # Register a tournament
    t = Tournament("WSOP 2011")
    # Enter all 5 players in WSOP 2011
    t.enterPlayer(p1)
    t.enterPlayer(p2)
    t.enterPlayer(p3)
    t.enterPlayer(p4)
    t.enterPlayer(p5)
    pairings = t.swissPairings()
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return three pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), 
        (pid5, pname5, pid6, pname6)] = pairings
    # All should have the same record, 0 0 0
    # Twilight should be paired with Fluttershy
    # Applejack should be paired with Pinkie
    # Darth Vader should have a bye
    correct_pairs = set([frozenset([p1, p2]), frozenset([p3, p4]), 
                        frozenset([p5, BYE])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), 
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "Before any matches have been played, players should still be "
            "paired.")
    print ("8. Before any matches played, players are correctly matched up.")


def testPairings():
    clearAll()
    # Register 5 players, saving their ids
    p1 = registerPlayer("Twilight Sparkle")
    p2 = registerPlayer("Fluttershy")
    p3 = registerPlayer("Applejack")
    p4 = registerPlayer("Pinkie Pie")
    p5 = registerPlayer("Darth Vader")
    # Register a tournament
    t = Tournament("WSOP 2011")
    # Enter all 5 players in WSOP 2011
    t.enterPlayer(p1)
    t.enterPlayer(p2)
    t.enterPlayer(p3)
    t.enterPlayer(p4)
    t.enterPlayer(p5)
    # Play a couple rounds
    t.reportMatch(p1, p2)   # First round - Twilight beats Fluttershy
    t.reportMatch(p4, p3)   # Pinkie beats Applejack
    t.reportBye(p5)         # Darth Vader gets a bye
    t.reportMatch(p4, p1)   # Second round - Pinkie beats Twilight
    t.reportDraw(p2, p5)    # Fluttershy draws with Darth Vader
    t.reportBye(p3)         # Applejack gets a bye
    pairings = t.swissPairings()
    if len(pairings) != 3:
        raise ValueError(
            "For five players, swissPairings should return three pairs.")
    [(pid1, pname1, pid2, pname2), (pid3, pname3, pid4, pname4), 
        (pid5, pname5, pid6, pname6)] = pairings
    # Pinkie at 2 0 0 should be paired with Darth Vader at 1 1 0
    # Twilight at 1 0 1 should be paired with Applejack at 1 0 1
    # Fluttershy at 0 1 1 should have a bye
    correct_pairs = set([frozenset([p4, p5]), frozenset([p1, p3]), 
                        frozenset([p2, BYE])])
    actual_pairs = set([frozenset([pid1, pid2]), frozenset([pid3, pid4]), 
                        frozenset([pid5, pid6])])
    if correct_pairs != actual_pairs:
        raise ValueError(
            "After two matches, players with no losses should be paired; "
            "players with one win and one loss should be paired; and the "
            "player in last place should get a bye.")
    print ("9. After two matches, players are correctly matched up.")


if __name__ == '__main__':
    clearAll()
    testDeleteMatches()
    testDelete()
    testCount()
    testRegister()
    testRegisterCountDelete()
    testStandingsBeforeMatches()
    testReportMatches()
    testEmptyPairings()
    testPairings()
    print "Success!  All tests pass!"


