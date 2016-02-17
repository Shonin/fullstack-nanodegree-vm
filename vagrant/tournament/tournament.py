#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()

def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT count(*) FROM players")
    count = c.fetchall()[0][0]
    DB.close()
    return count

def registerPlayer(name):
    """Adds a player to the tournament database.
     
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM standings")
    standings = c.fetchall()
    DB.close()
    return standings

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won #(+1 to wins +1 to matches played)
      loser:  the id number of the player who lost #(+1 to matches played)
    """
    DB = connect()
    c = DB.cursor()
    c.execute("INSERT INTO matches VALUES (%s, %s)", (winner,loser))
    DB.commit()
    DB.close()

def reportBye(bye):
    # register a fake player to handle the loss column of report match
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT id FROM players where name = 'bye';")
    byeId = c.fetchone()
    if byeId:
        c.execute("INSERT INTO matches VALUES (%s, %s)", (bye, byeId))
    else:
        registerPlayer('bye')
        c.execute("SELECT id FROM players where name = 'bye';")
        byeId = c.fetchone()
        c.execute("INSERT INTO matches VALUES (%s, %s)", (bye, byeId))
    DB.commit()
    DB.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name

    """
    DB = connect()
    c = DB.cursor()
    c.execute("SELECT * FROM standings")
    s = c.fetchall()
    DB.close()
    pairings = []
    for i in range(0, len(s), 2):
        pairings.append((s[i][0], s[i][1], s[i + 1][0], s[i + 1][1]))
    return pairings
        
