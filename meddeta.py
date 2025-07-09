import requests
from datetime import datetime
import os
import json
import time
from config import SONARR_URL, API_KEY, HEADERS, ROOT_FOLDER, QUALITY_PROFILE_ID


def get_id_from_title(title):
    """Get ID of the show from the title"""
    url = f"{SONARR_URL}/api/v3/series"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    series_list = response.json()

    for show in series_list:
        if show["title"].lower() == title.lower():
            return show["id"]
    
    return None

def add_to_sonnar(series_title):
    headers = {
        'X-Api-Key': API_KEY,
        'Content-Type': 'application/json'
    }

    # Search for the series in Sonarr's TVDB
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

def get_metadata(series_title, season_number=None, episode_number=None):
    """ Get id of the show """
    avalible_sonnar = True
    id = get_id_from_title(series_title)

    if not id:
        add_to_sonnar(series_title)
        id = get_id_from_title(series_title)
        avalible_sonnar = False

    if season_number is not None and episode_number is not None:
        time.sleep(10)
        # If a episde is previded get meddeta for that episode
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

            if avalible_sonnar == False:
             remove_from_sonnar(series_title)
            return episode_data

    else:
     """ Get Metadata """
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
     
     if avalible_sonnar == False:
        remove_from_sonnar(series_title)
 
     return anime_data


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    logging_file = "logs.txt"
    if not os.path.exists(logging_file): open(logging_file, 'a').close()

    new_log = f"{timestamp} - {message}\n"

    with open(logging_file, 'a') as file:
       file.write(new_log)

    print(new_log)   

def save_to_json(data, filename):
     # If the file exists, load its content
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Add new data
    existing_data.append(data)

    # Save back to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

metadata = get_metadata("Solo leveling", 1, 1)

save_to_json(metadata, "metadata.json")