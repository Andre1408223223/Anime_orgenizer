import requests
from datetime import datetime
import os
import time
from fuzzywuzzy import fuzz
from config import SONARR_URL, API_KEY, HEADERS, ROOT_FOLDER, QUALITY_PROFILE_ID


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

    if isinstance(series_title, list):
     avalible_sonnar = True
     episodes_data = []

     for serie in series_title:
        anime = serie['anime']
        season = serie['season']
        episode = serie['episode']

        id = get_id_from_title(anime)

        if not id:
         add_to_sonnar(anime)
         id = get_id_from_title(anime)
         avalible_sonnar = False


        url = f"{SONARR_URL}/api/v3/episode?seriesId={id}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        episodes = response.json() 

        for ep in episodes:
            if ep["seasonNumber"] == season and ep["episodeNumber"] == episode:
                episode_data = {
                    "title": ep.get("title", 'Unknown Title'),
                    "season": season,
                    "episode": episode,
                    "description": ep.get("overview", 'No description available.'),
                    "airDate": ep.get("airDate", 'Unknown Air Date'),
                }

                episodes_data.append(episode_data)

     if not avalible_sonnar:
        remove_from_sonnar(anime)   
        
     return  episodes_data        

    else: 
     avalible_sonnar = True
     id = get_id_from_title(series_title)

     if not id:
        add_to_sonnar(series_title)
        id = get_id_from_title(series_title)
        avalible_sonnar = False

     if season_number is not None and episode_number is not None:
        time.sleep(10)
        url = f"{SONARR_URL}/api/v3/episode?seriesId={id}"
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
                if not avalible_sonnar:
                    remove_from_sonnar(series_title)
                return episode_data
     else:
        url = f"{SONARR_URL}/api/v3/series/{id}"
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
        if not avalible_sonnar:
            remove_from_sonnar(series_title)
        return anime_data

def save_to_json(data, filename):
    import json, os
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    existing_data.append(data)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
 metadata = get_metadata_sonnar("My Instant Death Ability Is Overpowered", 1, 1)
 save_to_json(metadata, "metadata.json")
