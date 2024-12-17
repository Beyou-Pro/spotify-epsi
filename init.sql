CREATE TABLE playlists (
    pid VARCHAR(50) PRIMARY KEY,
    name TEXT NOT NULL,
    collaborative BOOLEAN DEFAULT FALSE,
    num_tracks INTEGER DEFAULT 0,
    num_followers INTEGER DEFAULT 0,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE tracks (
    track_uri VARCHAR(50) PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_uri VARCHAR(50) REFERENCES artists(artist_uri) ON DELETE CASCADE,
    album_uri VARCHAR(50) REFERENCES albums(album_uri) ON DELETE CASCADE,
    duration_ms INTEGER CHECK (duration_ms >= 0)
);


CREATE TABLE playlist_tracks (
    playlist_pid VARCHAR(50) REFERENCES playlists(pid) ON DELETE CASCADE,
    track_uri VARCHAR(50) REFERENCES tracks(track_uri) ON DELETE CASCADE,
    pos INTEGER,
    PRIMARY KEY (playlist_pid, track_uri),
    INDEX (playlist_pid, pos)
);


CREATE TABLE artists (
    artist_uri VARCHAR(50) PRIMARY KEY,
    artist_name TEXT NOT NULL
);

CREATE TABLE albums (
    album_uri VARCHAR(50) PRIMARY KEY,
    album_name TEXT NOT NULL,
    artist_uri VARCHAR(50) REFERENCES artists(artist_uri) ON DELETE CASCADE
);
