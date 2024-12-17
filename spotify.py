import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timezone
import os
import json
from concurrent.futures import ThreadPoolExecutor

conn = psycopg2.connect(
    dbname="database",
    user="user",
    password="your_password",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

def insert_data(json_data):
    artist_data = []
    album_data = []
    track_data = []
    playlist_data = []
    playlist_track_data = []

    for playlist in json_data.get('playlists', []):
        playlist_data.append((
            playlist['pid'],
            playlist['name'],
            playlist['collaborative'].lower() == 'true',
            playlist['num_tracks'],
            playlist['num_followers'],
            datetime.fromtimestamp(playlist['modified_at'], timezone.utc)
        ))

        for track in playlist.get('tracks', []):
            artist_data.append((
                track['artist_uri'],
                track['artist_name']
            ))

            album_data.append((
                track['album_uri'],
                track['album_name'],
                track['artist_uri']
            ))

            track_data.append((
                track['track_uri'],
                track['track_name'],
                track['artist_uri'],
                track['album_uri'],
                track['duration_ms']
            ))

            playlist_track_data.append((
                playlist['pid'],
                track['track_uri'],
                track['pos']
            ))

    if artist_data:
        execute_values(cur, """
            INSERT INTO artists (artist_uri, artist_name)
            VALUES %s
            ON CONFLICT (artist_uri) DO NOTHING
        """, artist_data)

    if album_data:
        execute_values(cur, """
            INSERT INTO albums (album_uri, album_name, artist_uri)
            VALUES %s
            ON CONFLICT (album_uri) DO NOTHING
        """, album_data)

    if track_data:
        execute_values(cur, """
            INSERT INTO tracks (track_uri, track_name, artist_uri, album_uri, duration_ms)
            VALUES %s
            ON CONFLICT (track_uri) DO NOTHING
        """, track_data)

    if playlist_data:
        execute_values(cur, """
            INSERT INTO playlists (pid, name, collaborative, num_tracks, num_followers, modified_at)
            VALUES %s
            ON CONFLICT (pid) DO NOTHING
        """, playlist_data)

    if playlist_track_data:
        execute_values(cur, """
            INSERT INTO playlist_tracks (playlist_pid, track_uri, pos)
            VALUES %s
            ON CONFLICT (playlist_pid, track_uri) DO NOTHING
        """, playlist_track_data)

    conn.commit()

def process_json_file(file_path):
    print(f"Processing file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            json_data = json.load(file)
            insert_data(json_data)
            print(f"Successfully processed {file_path}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_path}: {e}")

def process_json_files_in_folder(folder_path, max_workers=4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".json")]
        executor.map(process_json_file, json_files)

folder_path = "./data"
process_json_files_in_folder(folder_path)

cur.close()
conn.close()
