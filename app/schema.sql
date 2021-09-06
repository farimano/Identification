DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;

CREATE TABLE users (
	id_user INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT
);

CREATE TABLE events (
	id_event INTEGER PRIMARY KEY AUTOINCREMENT,
	id_user INTEGER NOT NULL,
	distance NUMERIC(7, 2),
	result INTEGER,
	error INTEGER,
	error_description TEXT
);

/* This is test values for dataset user  */
INSERT INTO users (name) VALUES ("E");
INSERT INTO users (name) VALUES ("L");
