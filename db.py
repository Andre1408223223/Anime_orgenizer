import sqlite3

def create_db():
 # Connect to or create the database
 conn = sqlite3.connect("shows.db")
 cursor = conn.cursor()
 
 # Create the shows table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS shows (
     id INTEGER PRIMARY KEY,
     title TEXT NOT NULL UNIQUE,
     description TEXT,
     rating INTEGER,
     status TEXT,
     poster_url TEXT
 )
 """)
 
 # Create the seasons table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS seasons (
     id INTEGER PRIMARY KEY,
     show_id INTEGER NOT NULL,
     season_number INTEGER NOT NULL,
     status TEXT,
     rating INTEGER,
     description TEXT,
     pster_url TEXT,
     FOREIGN KEY (show_id) REFERENCES shows(id)
 )
 """)
 
 # Create the episodes table
 cursor.execute("""
 CREATE TABLE IF NOT EXISTS episodes (
     id INTEGER PRIMARY KEY,
     show_id INTEGER NOT NULL,
     season_id INTEGER NOT NULL,
     title TEXT,
     episode_number INTEGER,
     rating INTEGER,
     description TEXT,
     air_date DATE,
     FOREIGN KEY (show_id) REFERENCES shows(id),
     FOREIGN KEY (season_id) REFERENCES seasons(id)
 )
 """)
 
 # Commit changes and close the connection
 conn.commit()
 conn.close()
 
 print("Database 'shows.db' created with tables: shows, seasons, episodes.")

def insert_db(data):
    conn = sqlite3.connect("shows.db")
    cursor = conn.cursor()

    # Insert show
    cursor.execute("""
    INSERT OR IGNORE INTO shows (title, description, rating, status, poster_url)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("description"),
        data.get("rating"),
        data.get("status"),
        data.get("poster_url")
    ))

    conn.commit()

    # Get the show ID
    cursor.execute("SELECT id FROM shows WHERE title = ?", (data["title"],))
    show_id = cursor.fetchone()[0]

    # Insert seasons
    for season in data.get("seasons", []):
        cursor.execute("""
        INSERT INTO seasons (show_id, season_number, status, rating, description, pster_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            show_id,
            season["season_number"],
            season.get("status"),
            season.get("rating"),
            season.get("description"),
            season.get("poster_url")
        ))

        season_id = cursor.lastrowid

        # Insert episodes
        for episode in season.get("episodes", []):
            cursor.execute("""
            INSERT INTO episodes (show_id, season_id, title, episode_number, rating, description, air_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                show_id,
                season_id,
                episode.get("title"),
                episode.get("episode_number"),
                episode.get("rating"),
                episode.get("description"),
                episode.get("air_date")
            ))

    conn.commit()
    conn.close()
    print(f"Inserted show '{data['title']}' with seasons and episodes.")


def run_query(sql_query):
    conn = sqlite3.connect("shows.db")
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        if sql_query.strip().lower().startswith("select"):
            results = cursor.fetchall()
            return results
        else:
            conn.commit()
            return None
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()

# Example usage
if __name__ == "__main__":
    # create_db()
    """ example_data = {
        "title": "Example Show",
        "description": "A great show about examples.",
        "rating": 8,
        "status": "Completed",
        "poster_url": "https://example.com/poster.jpg",
        "seasons": [
            {
                "season_number": 1,
                "status": "Completed",
                "rating": 7,
                "description": "Season 1 of the example show.",
                "poster_url": "https://example.com/s1.jpg",
                "episodes": [
                    {
                        "title": "Episode 1",
                        "episode_number": 1,
                        "rating": 8,
                        "description": "The first episode.",
                        "air_date": "2023-01-01"
                    },
                    {
                        "title": "Episode 2",
                        "episode_number": 2,
                        "rating": 7,
                        "description": "The second episode.",
                        "air_date": "2023-01-08"
                    }
                ]
            }
        ]
    }

    insert_db(example_data) """


    result  = run_query("SELECT id FROM shows WHERE title = 'Example Show'")
    if result:
     show_id = result[0][0] 
     
     result = run_query(f"SELECT * from episodes where show_id = {show_id}")

     print(result)
