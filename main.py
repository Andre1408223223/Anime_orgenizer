from torrent_orgenizer import get_episode_title_from_filename
from meddeta import get_metadata_sonnar
import time
import json
import os

files = ["[Altair] My Instant Death Ability is So Overpowered S01E01.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E02.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E03.mkv"]

def format_torent_file(files):
   data = []

   for file in files:
    # use function to clean up the name
    formated_name = get_episode_title_from_filename(file)

    if "[!]" in formated_name:
     break

    # split the title into anime and episde
    anime, episode = formated_name.split("-")

    # replace S and E so it only has numbers
    format_episode= episode.replace("S", "").replace("E", " ")

    # split into season and episde int
    season, episode = map(int, format_episode.split())

    entry = {
    'anime': anime,
    'season': season,
    'episode': episode
    }

    data.append(entry)

    time.sleep(5)

   data.append({'anime': anime})
   data.append({'anime': anime, 'season': season,})

   return data

formated_torrents = format_torent_file(files)

meta = get_metadata_sonnar(formated_torrents)

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

shows ,seasons, episodes = split_meta(meta)

show_title = shows[0]['title']
season_nm = seasons[0]['season']



show_folder_path = show_title
season_folder_path = os.path.join(show_folder_path, f"Season {str(season_nm)}")


os.makedirs(show_title, exist_ok=True)
os.makedirs(season_folder_path, exist_ok=True)

for episode in episodes:
   episode_title = episode['title']
   episode_nm = episode['episode_number']

   orignial_file = files[int(episode_nm) -1]

   _, ext = os.path.splitext(orignial_file)

   formatted_title = f"{show_title} - S{int(season_nm):02}E{int(episode_nm):02} - {episode_title}{ext}"

   os.rename(orignial_file, os.path.join(season_folder_path, formatted_title))



""" print("\n=== Shows ===")
print(json.dumps(shows, indent=4, ensure_ascii=False))

print("\n=== Seasons ===")
print(json.dumps(seasons, indent=4, ensure_ascii=False))

print("\n=== Episodes ===")
print(json.dumps(episodes, indent=4, ensure_ascii=False)) """