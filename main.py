from torrent_orgenizer import get_episode_title_from_filename
from meddeta import get_metadata_sonnar
import time
import json

""" files = ["[Altair] My Instant Death Ability is So Overpowered S01E10.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E02.mkv"]

data = [] """


""" Clean up title """
""" for file in files:
    # use function to clean up the name
    formated_name = get_episode_title_from_filename(file)

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

meta = get_metadata_sonnar(data)

print(meta) """


meta = [{'title': 'A Woman from the Past Appeared. Tomochika is Shocked to Her Core...', 'season': 1, 'episode': 10, 'description': 'Yogiri senses the gaze and murderous intent of someone different. To lure out the culprit, he heads into the city with Tomochika.', 'airDate': '2024-03-08'}, 
        {'title': 'My Guardian Angel Is So Overpowered, This Other World Is a Piece of Cake!', 'season': 1, 'episode': 2, 'description': 'Yogiri and Tomochika search for their classmates and arrive at a nearby town. Inside the city walls, the two meet a seemingly kind beastkin who has ulterior motives.', 'airDate': '2024-01-12'},
        {'title': 'My Instant Death Ability Is Overpowered', 'description': "Awaking to absolute chaos and carnage while on a school trip, Yogiri Takatou discovers that everyone in his class has been transported to another world! He had somehow managed to sleep through the entire ordeal himself, missing out on the Gift — powers bestowed upon the others by a mysterious Sage who appeared to transport them. Even worse, he and another classmate were ruthlessly abandoned by their friends, left as bait to distract a nearby dragon. Although not terribly bothered by the thought of dying, he reluctantly decides to protect his lone companion. After all, a lowly Level 1000 monster doesn't stand a chance against his secret power to invoke Instant Death with a single thought! If he can stay awake long enough to bother using it, that is...", 'year': 2024, 'genres': 'Adventure, Animation, Anime, Comedy, Fantasy', 'status': 'ended', 'rating': 6.2, 'poster_url': 'https://artworks.thetvdb.com/banners/v4/series/427883/posters/658b260f5cea0.jpg'}]

processed_entries = []

for entry in meta:
    genres = entry.get('genres', None)
    
    if genres:
        processed_entries.append({
            "type": "show",
            "title": entry.get('title', 'No title'),
            "description": entry.get('description', 'No description'),
            "year": entry.get('year', 'Unknown year'),
            "genres": entry.get('genres', 'Unknown genres'),
            "rating": entry.get('rating', 'No rating'),
            "poster_url": entry.get('poster_url', 'No poster URL')
        })
    else:
        processed_entries.append({
            "type": "episode",
            "title": entry.get('title', 'No title'),
            "episode_number": entry.get('episode', 'N/A'),
            "description": entry.get('description', 'No description'),
            "air_date": entry.get('airDate', 'Unknown date')
        })


with open("processed_entries.json", "w") as json_file:
    json.dump(processed_entries, json_file, indent=4)