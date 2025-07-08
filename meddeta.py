import requests
from config import SONARR_URL, API_KEY, HEADERS

def add_to_sonnar(series_title):
    pass

def get_metadata(series_title, season_number=None, episode_number=None):
    """ Get id of the show """
    url = f"{SONARR_URL}/api/v3/series"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    series_list = response.json() 

    id = None 
    for show in series_list:
        if show["title"].lower() == series_title.lower():
            id = show["id"]
            break 

    if not id:
        print(f"'{series_title}' not found in Sonarr.")
        add_to_sonnar(series_title)
        return None
    

    if season_number is not None and episode_number is not None:
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
 
 
     return anime_data


metadata = get_metadata("My Hero Academia")

print(metadata)

if "season" in metadata and "episode" in metadata:
    print("This is an episode.")
else:
    print("This is a show.")