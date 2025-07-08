import requests
from config import SONARR_URL, API_KEY, HEADERS

def add_to_sonnar(series_title):
    pass

def get_metadata(series_title):
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
        return None
    

    """ Get Metadata """
    url = f"{SONARR_URL}/api/v3/series/{id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    metadata = response.json()


    return metadata

metadata = get_metadata("My Hero Academia")


if metadata:
    anime_data = {
        "title": metadata.get('title', 'Unknown Title'),
        "description": metadata.get('overview', 'No description available.'),
        "year": metadata.get('year', 'Unknown Year'),
        "genres": ', '.join(metadata.get('genres', [])),
        "status": metadata.get('status', 'Unknown Status'),
        "rating": metadata.get('ratings', {}).get('value', 'N/A'),
        "poster_url": next((img['remoteUrl'] for img in metadata.get('images', []) if img.get('coverType') == 'poster'), None)
    }

    print(anime_data)