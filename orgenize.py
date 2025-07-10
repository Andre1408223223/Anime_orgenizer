from torrent_orgenizer import get_episode_title_from_filename
from meddeta import get_metadata_sonnar
import time

files = ["[Altair] My Instant Death Ability is So Overpowered S01E10.mkv", "[Altair] My Instant Death Ability is So Overpowered S01E02.mkv"]

""" Clean up title """
for file in files:
    # use function to clean up the name
    formated_name = get_episode_title_from_filename(file)

    # split the title into anime and episde
    anime, episode = formated_name.split("-")

    # replace S and E so it only has numbers
    format_episode= episode.replace("S", "").replace("E", " ")

    # split into season and episde int
    season, episode = map(int, format_episode.split())

    print(anime ,season, episode)

    time.sleep(1)