-- connect to the database
\c tournament

-- Drops all views and tables inside the database tournament in case
-- they already exist. If not it will skip over this task
DROP VIEW IF EXISTS standings;
DROP VIEW IF EXISTS wins;
DROP VIEW IF EXISTS loses;
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS players;

-- Creates the needed tables and columns
CREATE TABLE players (id SERIAL primary key, name TEXT);
CREATE TABLE matches (winner INT references players(id), 
					 loser INT references players(id));

-- Creates the view wins, which returns the players id, name, 
-- and number of wins that they have
CREATE VIEW wins AS
	SELECT players.id, players.name, count(matches.winner) AS wins
	FROM players
		LEFT JOIN matches ON players.id = matches.winner
	GROUP BY players.id, players.name;

-- Creates the view loses, which returns the players id, name, 
-- and number of loses that they have
CREATE VIEW loses AS
	SELECT players.id, players.name, count(matches.loser) AS loses
	FROM players
		LEFT JOIN matches ON players.id = matches.loser
	GROUP BY players.id, players.name;

-- Creates the view standings, which returns the players id, name, 
-- number of wins that they have, and the number of matches they've played in
CREATE VIEW standings AS
	SELECT players.id, players.name, wins.wins, 
	wins.wins + loses.loses AS matches
	FROM players
		LEFT JOIN wins ON players.id = wins.id
		LEFT JOIN loses ON players.id = loses.id
	GROUP BY players.id, players.name, wins.wins, loses.loses
	ORDER BY wins desc;


