import urllib.parse
from mutagen import File
import os

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
        artist = media_file.get('artist', ['Unknown Artist'])[0]
        genre = media_file.get('genre', ['Unknown Genre'])[0]
        return duration, artist, genre
    except Exception as e:
        print(f"Error getting metadata for {file_path}: {e}")
        return 0, 'Unknown Artist', 'Unknown Genre'

def extract_file_name_and_extension(line):
    try:
        start_index = line.find("file:///") + len("file:///")
        end_index = line.find("' successfully opened")
        file_path_encoded = line[start_index:end_index]
        file_path = urllib.parse.unquote(file_path_encoded)
        if os.path.isfile(file_path):
            return file_path
    except Exception as e:
        print(f"Error in extracting file path: {e}")
    return None

def count_media_plays(log_file_path, file_extensions):
    play_counts = {}
    total_durations = {}
    artist_genre_info = {}

    try:
        with open(log_file_path, 'r') as log_file:
            log_contents = log_file.readlines()
    except FileNotFoundError:
        return "Log file not found."
    except Exception as e:
        return f"An error occurred: {e}"

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

def main():
    print_ascii_art()
    log_file_path = input("Enter the path to your VLC log file: ")

    file_extensions = [".mp3", ".wav", ".ogg", ".flac"]

    play_counts, total_durations, artist_genre_info = count_media_plays(log_file_path, file_extensions)

    for file_path, count in play_counts.items():
        file_name = os.path.basename(file_path)
        total_playtime_minutes = total_durations[file_path] / 60
        artist, genre = artist_genre_info[file_path]
        print(f"'{file_name}' by {artist} ({genre}) was played {count} times. Total playtime: {total_playtime_minutes:.2f} minutes.")

if __name__ == "__main__":
    main()
