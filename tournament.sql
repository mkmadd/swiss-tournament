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

CREATE TABLE tournaments (
	id SERIAL PRIMARY KEY,
	name TEXT
);

CREATE TABLE tournament_players (
	tournament INT REFERENCES tournaments (id) ON DELETE CASCADE,
	player INT REFERENCES players (id) ON DELETE CASCADE
);

-- Every match has the id of the tournament it occurred in, a winner, a loser,
-- and a draw flag
CREATE TABLE matches (
	tournament INT REFERENCES tournaments (id),
	winner INT REFERENCES players (id),
	loser INT REFERENCES players (id),
	draw BOOLEAN
);

-- Returns a table with names and ids of players in specified tournament
CREATE OR REPLACE FUNCTION get_players_from_tourn(int)
RETURNS TABLE(id int, name text, tournament int) AS $$
	SELECT players.*, tournament 
	FROM tournament_players as tp LEFT JOIN players
	ON tp.player = players.id
	WHERE tp.tournament = $1;
$$ LANGUAGE SQL;

-- Returns a table with every match (listed twice for winner and loser)
-- with player id, name, winner id, loser id, whether it was a draw for the
-- specified tournament
CREATE OR REPLACE FUNCTION get_matches_from_tourn(int)
RETURNS TABLE(id int, name text, winner int, 
			  loser int, draw boolean, tournament int) AS $$
	SELECT id, name, winner, loser, draw, t_players.tournament
	FROM get_players_from_tourn($1) as t_players LEFT JOIN matches
	ON (t_players.id = matches.winner OR 
		t_players.id = matches.loser) AND 
		matches.tournament = t_players.tournament
$$ LANGUAGE SQL;

-- Returns a table listing all the players and their win/draw/loss record for
-- a specified tournament
CREATE OR REPLACE FUNCTION get_standings_from_tourn(int)
RETURNS TABLE(id int, name text, tournament int, 
		wins bigint, draws bigint, losses bigint) AS $$
	SELECT id, name, tournament,
		   SUM(CASE WHEN winner=id AND draw=FALSE THEN 1 ELSE 0 END) AS wins,
		   SUM(CASE WHEN (winner=id or loser=id) AND 
						 draw=TRUE THEN 1 ELSE 0 END) as draws,
		   SUM(CASE WHEN loser=id AND draw=FALSE THEN 1 ELSE 0 END) AS losses
		FROM get_matches_from_tourn($1)
	GROUP BY id, name, tournament;
$$ LANGUAGE SQL;

-- Returns table with list of player ids and their associated points (3 for a 
-- win, 1 for a draw, 0 for a loss) for a specified tournament
CREATE OR REPLACE FUNCTION get_player_points_from_tourn(int)
RETURNS TABLE(id int, points bigint) AS $$
	SELECT id,
		SUM(CASE WHEN winner=id AND draw=FALSE THEN 3
				 WHEN (winner=id OR loser=id) AND draw=TRUE THEN 1
				 ELSE 0 END) as points
	FROM get_matches_from_tourn($1)
	GROUP BY id
	ORDER BY points DESC;
$$ LANGUAGE SQL;

-- Returns table with players ids, name, and opponent for a specified tournament
CREATE OR REPLACE FUNCTION get_player_opponents_from_tourn(int)
RETURNS TABLE(id int, name text, opponent int) AS $$
	SELECT id, name,
		   CASE WHEN winner=id THEN loser
				WHEN loser = id THEN winner END AS opponent
	FROM get_matches_from_tourn($1);
$$ LANGUAGE SQL;

-- Returns table with player id and their opponents' points from a specified
-- tournament
CREATE OR REPLACE FUNCTION get_opponent_points_from_tourn(int)
RETURNS TABLE(id int, points bigint) AS $$
	SELECT A.id, SUM(B.points::int) as points
	FROM get_player_opponents_from_tourn($1) A
	JOIN get_player_points_from_tourn($1) B
	ON A.opponent = B.id
	GROUP BY A.id;
$$ LANGUAGE SQL;

-- Returns table with each player id occurring once with array of opponents'
-- ids for a given tournament
CREATE OR REPLACE FUNCTION aggregate_player_opponents_from_tourn(int)
RETURNS TABLE(id int, opponents int[]) AS $$
	SELECT id, array_agg(opponent) 
	FROM get_player_opponents_from_tourn($1)
	GROUP BY id;
$$ LANGUAGE SQL;

-- Returns table with all player ids, names, wins, draws, losses, opponents,
-- and opponent points for a specified tournament
CREATE OR REPLACE FUNCTION get_info_for_pairing_from_tourn(int)
RETURNS TABLE(id int, name text, 
			  wins bigint, draws bigint, losses bigint, 
			  opponents int[], points bigint) AS $$
	SELECT id, name, wins, draws, losses, opponents, points FROM
		(SELECT * 
		FROM get_standings_from_tourn($1)
		LEFT JOIN get_opponent_points_from_tourn($1)
		USING (id)) AS standings 
	LEFT JOIN aggregate_player_opponents_from_tourn($1)
	USING (id)                
	ORDER BY wins DESC, draws DESC, points DESC;
$$ LANGUAGE SQL;

-- After setup, initialize with first player as 'bye'
INSERT INTO players (name) VALUES ('bye');