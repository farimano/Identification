DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS positions;

CREATE TABLE users (
	id_user INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	id_pos INTEGER
);

CREATE TABLE events (
	id_event INTEGER PRIMARY KEY AUTOINCREMENT,
	id_user INTEGER NOT NULL,
	recognition_degree NUMERIC(7, 2),
	number_faces INTEGER,
	error INTEGER,
	error_description TEXT
);

CREATE TABLE positions (
	id_pos INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT
);

/* This is test values for table positions  */
INSERT INTO positions (title) VALUES ("Developer");
INSERT INTO positions (title) VALUES ("HR-manager");
INSERT INTO positions (title) VALUES ("Security");


/* This is test values for table users  */
INSERT INTO users (name, id_pos) VALUES ("Alice", 1);
INSERT INTO users (name, id_pos) VALUES ("Viktor", 2);
INSERT INTO users (name) VALUES ("Vladimir");
