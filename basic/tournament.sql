-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    winner INT REFERENCES players (id),
    loser INT REFERENCES players (id)
);

-- Return a table of player ids, names, wins, and matches played, ranked by
-- number of wins
CREATE OR REPLACE VIEW player_standings AS
    SELECT id, name, 
           SUM(CASE WHEN winner=id THEN 1 ELSE 0 END) AS wins,
           SUM(CASE WHEN loser=id OR 
                   winner=id THEN 1 ELSE 0 END) AS matches
    FROM (SELECT players.id, name, winner, loser
        FROM players LEFT JOIN matches
        ON players.id = matches.winner OR players.id = matches.loser
    ) AS temp
    GROUP BY id, name
    ORDER BY wins DESC;

-- Following two views are used to pair players up.  A simple pairing scheme,
-- it pairs each player with the player beneath them in the standings (even
-- players vs odd players), without regard for whether they've already played
-- or not.
CREATE OR REPLACE VIEW odd_players AS
    SELECT *
    FROM (SELECT *, row_number() OVER (ORDER BY wins DESC) AS rnum
        FROM player_standings
        ORDER BY wins DESC) as temp
    WHERE MOD(rnum, 2) = 1;

CREATE OR REPLACE VIEW even_players AS
    SELECT *
    FROM (SELECT *, row_number() OVER (ORDER BY wins DESC) AS rnum
        FROM player_standings
        ORDER BY wins DESC) as temp
    WHERE MOD(rnum, 2) = 0;