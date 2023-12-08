import sqlite3
import pandas as pd
import os
import urllib.parse
from mutagen import File

def get_file_path():
    return input("enter file path (.db or .txt): ")

def convert_duration(milliseconds):
    seconds = int(milliseconds / 1000)
    minutes = seconds // 60
    seconds %= 60
    return f"{minutes} min {seconds} sec"

def calculate_total_play_time(duration_milliseconds, play_count):
    total_duration_seconds = (duration_milliseconds / 1000) * play_count
    total_duration_minutes = total_duration_seconds / 60
    return round(total_duration_minutes, 2)

def query_database(db_path):
    conn = sqlite3.connect(db_path)
    query = """
    SELECT m.title AS SongTitle, a.name AS ArtistName, g.name AS Genre, m.play_count, m.duration
    FROM Media m
    LEFT JOIN Artist a ON m.artist_id = a.id_artist
    LEFT JOIN Genre g ON m.genre_id = g.id_genre
    WHERE m.play_count > 0
    ORDER BY m.play_count DESC;
    """
    result_df = pd.read_sql_query(query, conn)
    result_df['TotalDurationPlayed'] = result_df.apply(
        lambda row: calculate_total_play_time(row['duration'], row['play_count']), axis=1)
    conn.close()
    return result_df

def print_ascii_art():
    print("██╗    ██╗██████╗  █████╗ ██████╗ ██████╗ ██╗   ██╗")
    print("██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝")
    print("██║ █╗ ██║██████╔╝███████║██████╔╝██████╔╝ ╚████╔╝ ")
    print("██║███╗██║██╔══██╗██╔══██║██╔═══╝ ██╔═══╝   ╚██╔╝  ")
    print("╚███╔███╔╝██║  ██║██║  ██║██║     ██║        ██║   ")
    print(" ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝        ╚═╝   ")
    print()

def get_media_metadata(file_path):
    try:
        media_file = File(file_path)
        duration = media_file.info.length if media_file else 0
        artist = media_file.get('artist', ['unknown artist'])[0]
        genre = media_file.get('genre', ['unknown genre'])[0]
        return duration, artist, genre
    except Exception as e:
        print(f"error getting metadata for {file_path}: {e}")
        return 0, 'unknown artist', 'unknown genre'

def extract_file_name_and_extension(line):
    try:
        start_index = line.find("file:///") + len("file:///")
        end_index = line.find("' successfully opened")
        file_path_encoded = line[start_index:end_index]
        file_path = urllib.parse.unquote(file_path_encoded)
        if os.path.isfile(file_path):
           return file_path
    except Exception as e:
        print(f"error in extracting file path: {e}")
    return None

def count_media_plays(log_file_path, file_extensions):
    play_counts = {}
    total_durations = {}
    artist_genre_info = {}

    try:
        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.readlines()
    except FileNotFoundError:
        print("log file not found.")
        return
    except Exception as e:
        print(f"an error occurred: {e}")
        return

    for line in log_contents:
        if line.startswith("main debug: `file:///") and line.endswith("' successfully opened\n"):
            if any(ext in line for ext in file_extensions):
                file_path = extract_file_name_and_extension(line)
                if file_path:
                    play_counts[file_path] = play_counts.get(file_path, 0) + 1
                    if file_path not in total_durations:
                        duration, artist, genre = get_media_metadata(file_path)
                        total_durations[file_path] = duration
                        artist_genre_info[file_path] = (artist, genre)
                    else:
                        total_durations[file_path] += duration

    return play_counts, total_durations, artist_genre_info

def process_log_file(file_path):
    file_extensions = [".mp3", ".wav", ".ogg", ".flac"]  

    play_counts, total_durations, artist_genre_info = count_media_plays(file_path, file_extensions)

    for file_path, count in play_counts.items():
        file_name = os.path.basename(file_path)
        total_playtime_minutes = total_durations[file_path] / 60
        artist, genre = artist_genre_info[file_path]
        print(f"'{file_name}' by {artist} ({genre}) was played {count} times. total playtime: {total_playtime_minutes:.2f} minutes.")

def main():
    print_ascii_art()
    file_path = get_file_path()

    if not os.path.exists(file_path):
        print("File not found.")
        return

    if file_path.endswith('.db'):
        song_details = query_database(file_path)
        for index, row in song_details.iterrows():
            print(f"'{row['SongTitle']}' by {row['ArtistName']} ({row['Genre']}) was played {row['play_count']} times. Total playtime: {row['TotalDurationPlayed']} min")
    elif file_path.endswith('.txt'):
        process_log_file(file_path)
    else:
        print("invalid file type. .db or .txt files only")

if __name__ == "__main__":
    main()
