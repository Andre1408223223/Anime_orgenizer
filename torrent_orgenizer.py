import re
from guessit import guessit
from jikanpy import Jikan
import time

jikan = Jikan()

def preprocess_filename(name: str) -> str:
    # Fix 'S2 - 01' to 'S02E01' for better parsing
    return re.sub(
        r'S(\d+)\s*-\s*(\d+)',
        lambda m: f"S{int(m.group(1)):02}E{int(m.group(2)):02}",
        name
    )

def get_episode_title_from_filename(raw_filename: str) -> str:
    raw = preprocess_filename(raw_filename)
    info = guessit(raw)
    parsed_title = info.get('title')
    season = info.get('season', 1)
    episode = info.get('episode')

    if not parsed_title or not episode:
        return f"[!] Could not parse season/episode from: {raw_filename}"

    try:
        # 1) Search anime by parsed title to get MAL ID + English series title
        search = jikan.search('anime', parsed_title, page=1)
        entries = search.get('results') or search.get('data') or []
        if not entries:
            raise ValueError("No search results")

        mal_entry = entries[0]
        mal_id      = mal_entry['mal_id']
        # prefer the 'title_english' field if present
        official_title = mal_entry.get('title_english') or mal_entry.get('title')

        # 2) Grab this single episode’s info
        ep_data = jikan.anime_episode_by_id(anime_id=mal_id, episode_id=episode)

    except Exception as e:
        print(f"[!] Jikan lookup failed: {e}")
        # Fallback to parsed title + generic episode
        official_title = parsed_title

    # 3) Return with English series title, SxxExx and the English episode title
    return f"{official_title} - S{season:02}E{episode:02}"

# Test example
if __name__ == "__main__":
    raw = "[Altair] My Instant Death Ability is So Overpowered S01E01.mkv"
    print(get_episode_title_from_filename(raw))
