from torrent_orgenizer import get_episode_title_from_filename
from meddeta import get_metadata_sonnar
import time
from pathlib import Path
import os
from datetime import datetime
import re

download_folder = Path(r"C:\Users\Driek\Documents\Python_scripts\Projects\Anime_orgenizer\files\downloads")
orgenized_folder = Path(r"C:\Users\Driek\Documents\Python_scripts\Projects\Anime_orgenizer\files\orgenized\tv-shows")

def remove_procced_anime(folder):
    media_files = [f for f in folder.iterdir() if f.is_file() and is_media_file(f)]

    if not media_files:
        os.rmdir(folder)

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

def move_to_orgenize_folder():
    pass

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    logging_file = "logs.txt"
    if not os.path.exists(logging_file):
        open(logging_file, 'a').close()
    new_log = f"{timestamp} - {message}\n"
    with open(logging_file, 'a') as file:
        file.write(new_log)
    print(new_log)

def list_media_files(folder):
    media_extensions = {".mp4", ".mkv", ".avi", ".mp3", ".wav", ".flac", ".mov"}
    return [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in media_extensions]

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

def is_media_file(file_path):
    return file_path.suffix.lower() in {".mp4", ".mkv", ".avi", ".mp3", ".wav", ".flac", ".mov"}

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

# MAIN LOOP
if not download_folder.exists():
    log(f"Download folder does not exist: {download_folder}")
else:
    for anime_folder in download_folder.iterdir():
        if anime_folder.is_dir():
            process_folder(anime_folder)




# files = ["[Altair] My Instant Death Ability is So Overpowered S01E01.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E02.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E03.mkv"]

# def format_torent_file(files):
#    data = []

#    for file in files:
#     # use function to clean up the name
#     formated_name = get_episode_title_from_filename(file)

#     if "[!]" in formated_name:
#      break

#     # split the title into anime and episde
#     anime, episode = formated_name.split("-")

#     # replace S and E so it only has numbers
#     format_episode= episode.replace("S", "").replace("E", " ")

#     # split into season and episde int
#     season, episode = map(int, format_episode.split())

#     entry = {
#     'anime': anime,
#     'season': season,
#     'episode': episode
#     }

#     data.append(entry)

#     time.sleep(5)

#    data.append({'anime': anime})
#    data.append({'anime': anime, 'season': season,})

#    return data

# formated_torrents = format_torent_file(files)

# meta = get_metadata_sonnar(formated_torrents)

# def split_meta(meta):
#   shows = []
#   seasons = []
#   episodes = []
  
#   for entry in meta:
#       genres = entry.get('genres', None)
#       season = entry.get('season', None)
#       episdoe = entry.get('episode', None)
      
#       if genres:
#           # show
#           entry = {
#               "title": entry.get('title', 'No title'),
#               "description": entry.get('description', 'No description'),
#               "year": entry.get('year', 'Unknown year'),
#               "genres": entry.get('genres', 'Unknown genres'),
#               "rating": entry.get('rating', 'No rating'),
#               "poster_url": entry.get('poster_url', 'No poster URL')
#           }
#           shows.append(entry)
  
#       elif season is not None and episdoe is not None:
#           # Episdoe
#           entry = {
#               "title": entry.get('title', 'No title'),
#               "episode_number": entry.get('episode', 'N/A'),
#               "description": entry.get('description', 'No description'),
#               "air_date": entry.get('airDate', 'Unknown date')
#           }
  
#           episodes.append(entry)
  
#       else:
#           # Season
#           entry = {
#               'season': entry.get('season', 'N/A'),
#               'total_episodes': entry.get('total_episodes', 'N/A')
#           }
  
#           seasons.append(entry)

#   return shows, seasons, episodes         

# shows ,seasons, episodes = split_meta(meta)

# show_title = shows[0]['title']
# season_nm = seasons[0]['season']



# show_folder_path = show_title
# season_folder_path = os.path.join(show_folder_path, f"Season {str(season_nm)}")


# os.makedirs(show_title, exist_ok=True)
# os.makedirs(season_folder_path, exist_ok=True)

# for episode in episodes:
#    episode_title = episode['title']
#    episode_nm = episode['episode_number']

#    orignial_file = files[int(episode_nm) -1]

#    _, ext = os.path.splitext(orignial_file)

#    formatted_title = f"{show_title} - S{int(season_nm):02}E{int(episode_nm):02} - {episode_title}{ext}"

#    os.rename(orignial_file, os.path.join(season_folder_path, formatted_title))



""" print("\n=== Shows ===")
print(json.dumps(shows, indent=4, ensure_ascii=False))

print("\n=== Seasons ===")
print(json.dumps(seasons, indent=4, ensure_ascii=False))

print("\n=== Episodes ===")
print(json.dumps(episodes, indent=4, ensure_ascii=False)) """