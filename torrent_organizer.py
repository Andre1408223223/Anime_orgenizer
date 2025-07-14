import os, re, time
from pathlib import Path
from datetime import datetime
import requests
from fuzzywuzzy import fuzz
from guessit import guessit
from jikanpy import Jikan
import sqlite3
import json
from config import SONARR_URL, API_KEY, HEADERS, ROOT_FOLDER, QUALITY_PROFILE_ID

jikan = Jikan()

def log():
   pass
   
""" Anime/Shows """
def get_metadata_sonnar(series_title, season_number=None, episode_number=None):
    def log(message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        logging_file = "logs.txt"
        if not os.path.exists(logging_file): open(logging_file, 'a').close()
        new_log = f"{timestamp} - {message}\n"
        with open(logging_file, 'a') as file:
            file.write(new_log)
        print(new_log)

    def get_id_from_title(title, threshold=80):
     url = f"{SONARR_URL}/api/v3/series"
     response = requests.get(url, headers=HEADERS)
     response.raise_for_status()
     series_list = response.json()
 
     best_match = None
     highest_score = 0
 
     for show in series_list:
         score = fuzz.token_set_ratio(show["title"].lower(), title.lower())
         if score > highest_score and score >= threshold:
             highest_score = score
             best_match = show
 
     if best_match:
         return best_match["id"]
     return None

    def add_to_sonnar(series_title):
        headers = {
            'X-Api-Key': API_KEY,
            'Content-Type': 'application/json'
        }
        search_url = f'{SONARR_URL}/api/v3/series/lookup?term={series_title}'
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200 or not response.json():
            log(f"Series '{series_title}' not found.")
            return
        series_data = response.json()[0]
        payload = {
            'tvdbId': series_data['tvdbId'],
            'title': series_data['title'],
            'qualityProfileId': QUALITY_PROFILE_ID,
            'titleSlug': series_data['titleSlug'],
            'images': series_data['images'],
            'seasons': [{'seasonNumber': s['seasonNumber'], 'monitored': False} for s in series_data['seasons']],
            'monitored': False,
            'rootFolderPath': ROOT_FOLDER,
            'addOptions': {
                'searchForMissingEpisodes': False,
                'monitor': 'none'
            }
        }
        add_url = f'{SONARR_URL}/api/v3/series'
        add_response = requests.post(add_url, json=payload, headers=headers)
        if add_response.status_code != 201:
            log(f"Failed to add series: {add_response.status_code} - {add_response.text}")

    def remove_from_sonnar(series_title):
        id = get_id_from_title(series_title)
        if not id:
            log(f"Series '{series_title}' not found in Sonarr.")
            return
        url = f"{SONARR_URL}/api/v3/series/{id}?deleteFiles=false"
        response = requests.delete(url, headers=HEADERS)
        if response.status_code != 200:
            log(f"Failed to remove '{series_title}': {response.status_code} - {response.text}")

    def get_metadata_show(show_id):
       url = f"{SONARR_URL}/api/v3/series/{show_id}"
       response = requests.get(url, headers=HEADERS)
       response.raise_for_status()
       metadata = response.json()
       anime_data = {
           "title": metadata.get('title', 'Unknown Title'),
           "description": metadata.get('overview', 'No description available.'),
           "year": metadata.get('year', 'Unknown Year'),
           "genres": ', '.join(metadata.get('genres', [])),
           "status": metadata.get('status', 'Unknown Status'),
           "rating": metadata.get('ratings', {}).get('value', 'N/A'),
           "poster_url": next((img['remoteUrl'] for img in metadata.get('images', []) if img.get('coverType') == 'poster'), None)
       }

       return anime_data

    def get_metadata_episode(show_id, season_number, episode_number):
       url = f"{SONARR_URL}/api/v3/episode?seriesId={show_id}"
       response = requests.get(url, headers=HEADERS)
       response.raise_for_status()
       episodes = response.json()
       for ep in episodes:
           if ep["seasonNumber"] == season_number and ep["episodeNumber"] == episode_number:
               episode_data = {
                   "title": ep.get("title", 'Unknown Title'),
                   "season": season_number,
                   "episode": episode_number,
                   "description": ep.get("overview", 'No description available.'),
                   "airDate": ep.get("airDate", 'Unknown Air Date'),
               }
               return episode_data

    def get_metadata_season(show_id, target_season_number):
     url = f"{SONARR_URL}/api/v3/series/{show_id}"
     response = requests.get(url, headers=HEADERS)
     response.raise_for_status()
     metadata = response.json()
 
     seasons = metadata.get('seasons', [])
     for season in seasons:
         season_num = int(season.get('seasonNumber', -1))
 
         if season_num == int(target_season_number):
             statistics = season.get('statistics', {})
             total_episodes = int(statistics.get('totalEpisodeCount', 0))
             episode_file_count = int(statistics.get('episodeFileCount', 0))
             percent_of_episodes = float(statistics.get('percentOfEpisodes', 0.0))
 
             # Return as a dictionary for clarity
             return {
                 'season': season_num,
                 'total_episodes': total_episodes,
             }
 
     return None

    if isinstance(series_title, list):
     avalible_sonnar = True
     data = []

     for serie in series_title:
        anime = serie['anime']
        season = serie.get('season', None)   
        episode = serie.get('episode', None) 

        id = get_id_from_title(anime)

        if not id:
         add_to_sonnar(anime)
         id = get_id_from_title(anime)
         avalible_sonnar = False

        if season and episode is not None:
           #Episdoe
           time.sleep(10)
           episode_data = get_metadata_episode(id, season, episode)
           data.append(episode_data)

        elif season is not None and episode is None:
          #Season
          time.sleep(10)
          season_data = get_metadata_season(id, season)
          data.append(season_data) 

        else:
           anime_data = get_metadata_show(id)
           data.append(anime_data)   

     if not avalible_sonnar:
        remove_from_sonnar(anime)   
        
     return  data        

    else: 
     avalible_sonnar = True
     id = get_id_from_title(series_title)

     if not id:
        add_to_sonnar(series_title)
        id = get_id_from_title(series_title)
        avalible_sonnar = False

     if season_number is not None and episode_number is not None:
        time.sleep(10)
        anime_data = get_metadata_episode(id, season_number, episode_number)

     elif season_number is not None and episode_number is None:
          time.sleep(10)
          season_data = get_metadata_season(id, season)
          data.append(season_data) 

     else:
        anime_data = get_metadata_show(id)
     
     if not avalible_sonnar:
            remove_from_sonnar(series_title)

     return anime_data       

def get_episode_title_from_filename(raw_filename: str) -> str:
    # Step 1: Fix 'S2 - 01' to 'S02E01' for better parsing
    name = re.sub(
        r'S(\d+)\s*-\s*(\d+)',
        lambda m: f"S{int(m.group(1)):02}E{int(m.group(2)):02}",
        raw_filename
    )
    
    # Step 2: Parse with guessit
    info = guessit(name)
    parsed_title = info.get('title')
    season = info.get('season', 1)
    episode = info.get('episode')

    if not parsed_title or not episode:
        return f"[!] Could not parse season/episode from: {raw_filename}"

    try:
        # Step 3: Search anime by parsed title to get MAL ID + English series title
        search = jikan.search('anime', parsed_title, page=1)
        entries = search.get('results') or search.get('data') or []
        if not entries:
            raise ValueError("No search results")

        mal_entry = entries[0]
        mal_id = mal_entry['mal_id']
        official_title = mal_entry.get('title_english') or mal_entry.get('title')

        # Step 4: Grab this single episode’s info
        ep_data = jikan.anime_episode_by_id(anime_id=mal_id, episode_id=episode)

    except Exception as e:
        print(f"[!] Jikan lookup failed: {e}")
        official_title = parsed_title

    # Step 5: Return formatted title with season and episode
    return f"{official_title} - S{season:02}E{episode:02}"

def organize_anime_downloads(download_folder: Path, orgenized_folder: Path):
    def remove_procced_anime(folder):
     media_files = [f for f in folder.iterdir() if f.is_file() and is_media_file(f)]

     if media_files:
         return
 
     # Remove empty subfolders
     for sub in folder.iterdir():
         if sub.is_dir():
             try:
                 if not any(sub.iterdir()):
                     sub.rmdir()
             except Exception as e:
                 print(f"Failed to remove subfolder {sub}: {e}")
 
     # Try to remove the main folder if it's now empty
     try:
         if not any(folder.iterdir()):
             folder.rmdir()
     except Exception as e:
        print(f"Failed to remove folder {folder}: {e}")

    def split_meta(meta):
     shows = []
     seasons = []
     episodes = []
     
     for entry in meta:
         genres = entry.get('genres', None)
         season = entry.get('season', None)
         episdoe = entry.get('episode', None)
         
         if genres:
             # show
             entry = {
                 "title": entry.get('title', 'No title'),
                 "description": entry.get('description', 'No description'),
                 "year": entry.get('year', 'Unknown year'),
                 "genres": entry.get('genres', 'Unknown genres'),
                 "rating": entry.get('rating', 'No rating'),
                 "poster_url": entry.get('poster_url', 'No poster URL')
             }
             shows.append(entry)
     
         elif season is not None and episdoe is not None:
             # Episdoe
             entry = {
                 "title": entry.get('title', 'No title'),
                 "episode_number": entry.get('episode', 'N/A'),
                 "description": entry.get('description', 'No description'),
                 "air_date": entry.get('airDate', 'Unknown date')
             }
     
             episodes.append(entry)
     
         else:
             # Season
             entry = {
                 'season': entry.get('season', 'N/A'),
                 'total_episodes': entry.get('total_episodes', 'N/A')
             }
     
             seasons.append(entry)
   
     return shows, seasons, episodes 

    def is_media_file(file_path):
     return file_path.suffix.lower() in {".mp4", ".mkv", ".avi", ".mp3", ".wav", ".flac", ".mov"}

    def format_torent_file(files):
        data = []
    
        for file in files:
            try:
                formated_name = get_episode_title_from_filename(file)
    
                if not formated_name or "[!]" in formated_name:
                    log(f"Skipped malformed or flagged filename: {file}")
                    continue
    
                anime, episode = formated_name.split("-")
                format_episode = episode.replace("S", "").replace("E", " ")
                season, episode = map(int, format_episode.split())
    
                entry = {
                    'anime': anime.strip(),
                    'season': season,
                    'episode': episode
                }
    
                data.append(entry)
                time.sleep(5)
    
            except Exception as e:
                log(f"Error processing file '{file}': {e}")
                continue
    
        if data:
            last = data[-1]
            anime = last.get("anime", "Unknown")
            season = last.get("season", 1)
    
            data.insert(0, {'anime': anime})
            data.insert(1, {'anime': anime, 'season': season})
            
        return data

    def move_episode_file(orignial_file, season_folder_path, show_title, season_nm, episode):
        episode_title = episode['title']
        episode_nm = episode['episode_number']
    
        _, ext = os.path.splitext(orignial_file)
    
        clean_title = re.sub(r'[<>:"/\\|?*]', '', episode_title)
        formatted_title = f"{show_title} - S{int(season_nm):02}E{int(episode_nm):02} - {clean_title}{ext}"
    
        os.rename(orignial_file, os.path.join(season_folder_path, formatted_title))

    def process_files(files):
        filenames = [f.name for f in files]
        formated_torrents = format_torent_file(filenames)
    
        meta = get_metadata_sonnar(formated_torrents)
    
        shows, seasons, episodes = split_meta(meta)

        save_metadata_to_db(shows, seasons, episodes)
    
        show_title = shows[0]['title']
        season_nm = seasons[0]['season']
    
        show_folder_path = os.path.join(orgenized_folder, show_title)
        season_folder_path = os.path.join(show_folder_path, f"Season {str(season_nm)}")
    
        os.makedirs(show_folder_path, exist_ok=True)
        os.makedirs(season_folder_path, exist_ok=True)
    
        for episode in episodes:
            episode_nm = episode['episode_number']
            orignial_file = files[int(episode_nm) - 1]
    
            move_episode_file(orignial_file, season_folder_path, show_title, season_nm, episode)
    
    def process_folder(folder: Path):
        media_files = [f for f in folder.iterdir() if f.is_file() and is_media_file(f)]
    
        if media_files:
            process_files(media_files)
        else:
            season_folders = [f for f in folder.iterdir() if f.is_dir()]
    
            if season_folders:
                for season in season_folders:
                    season_files = [f for f in season.rglob("*") if f.is_file() and is_media_file(f)]
                    if season_files:
                        process_files(season_files)
            else:
                log(f"No media files found in '{folder.name}'.")
    
        remove_procced_anime(folder)        

    # MAIN LOOP inside the function
    if not download_folder.exists():
        log(f"Download folder does not exist: {download_folder}")
    else:
        for anime_folder in download_folder.iterdir():
            if anime_folder.is_dir():
                process_folder(anime_folder)

def save_metadata_to_db(shows, seasons, episodes, db_name = "media.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL UNIQUE,
            description TEXT,
            year DATE,
            genres TEXT,
            rating INT,
            poster_url TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INT,
            season INT,
            total_episodes INT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INT,
            season_id INT,
            title TEXT,
            episode_number INT,
            description TEXT,
            air_date DATE
        )
    ''')

    # Insert the one show
    show = shows[0]
    cursor.execute('''
    INSERT OR IGNORE INTO shows (title, description, year, genres, rating, poster_url)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        show["title"],
        show["description"],
        show["year"],
        json.dumps(show["genres"]), 
        show["rating"],
        show["poster_url"]
    ))

    # Check if inserted or fetch existing
    if cursor.lastrowid != 0:
        show_id = cursor.lastrowid
    else:
        cursor.execute("SELECT id FROM shows WHERE title = ? AND year = ?", (show["title"], show["year"]))
        show_id = cursor.fetchone()[0]

    # Insert the one season
    season = seasons[0]
    cursor.execute('''
        INSERT INTO seasons (show_id, season, total_episodes)
        VALUES (?, ?, ?)
    ''', (
        show_id,
        season["season"],
        season["total_episodes"]
    ))
    season_id = cursor.lastrowid

    # Insert all episodes
    for episode in episodes:
        cursor.execute('''
            INSERT INTO episodes (show_id, season_id, title, episode_number, description, air_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            show_id,
            season_id,
            episode["title"],
            episode["episode_number"],
            episode["description"],
            episode["air_date"]
        ))

    conn.commit()
    conn.close()

def main():
    download_folder = Path(r"C:\Users\Driek\Documents\Python_scripts\Projects\Anime_orgenizer\files\downloads")
    orgenized_folder = Path(r"C:\Users\Driek\Documents\Python_scripts\Projects\Anime_orgenizer\files\orgenized\tv-shows")

    while True:
        organize_anime_downloads(download_folder, orgenized_folder)
        time.sleep(60)  # wait 60 seconds before checking again


if __name__ == "__main__":
    main()