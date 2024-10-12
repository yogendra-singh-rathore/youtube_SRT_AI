import sqlite3
import os

def database_execution():
    # Define the database path
    database_path = os.path.join('./output/database', 'youtube.db')
    
    # Check if the database already exists
    if not os.path.exists(database_path):
        # Connect to SQLite database (or create it if it doesn't exist)
        with sqlite3.connect(database_path) as conn:
            cursor = conn.cursor()

            # Create video_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_title TEXT NOT NULL,
                video_url TEXT NOT NULL,
                video_description TEXT
            )
            ''')

            # Create subtitle_language_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS subtitle_language_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                language TEXT UNIQUE
            )
            ''')

            # Insert languages into subtitle_language_table
            languages = ["English", "Hindi", "German"]
            cursor.executemany('INSERT INTO subtitle_language_table (language) VALUES (?)', ((lang,) for lang in languages))

            # Create playlist_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_name TEXT DEFAULT 'None'
            )
            ''')

            # Create status_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                status TEXT NOT NULL
            )
            ''')

            # Insert statuses into status_table
            statuses = ['Planning', 'Scripting', 'Recording', 'Editing', 'Private', 'Public', 'Unlisted']
            cursor.executemany('INSERT INTO status_table (status) VALUES (?)', ((status,) for status in statuses))

            # Create video_status
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_status (
                video_id INTEGER,
                status_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES video_table(id),
                FOREIGN KEY (status_id) REFERENCES status_table(id)
            )
            ''')

            # Create playlist_status
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_status (
                playlist_id INTEGER,
                status_id INTEGER,
                FOREIGN KEY (playlist_id) REFERENCES playlist_table(id),
                FOREIGN KEY (status_id) REFERENCES status_table(id)
            )
            ''')

            # Create video_playlist_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_playlist_table (
                video_id INTEGER,
                playlist_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES video_table(id),
                FOREIGN KEY (playlist_id) REFERENCES playlist_table(id)
            )
            ''')

            # Create videoLanguage_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS videoLanguage_table (
                video_id INTEGER,
                subtitle_id INTEGER,
                FOREIGN KEY (video_id) REFERENCES video_table(id),
                FOREIGN KEY (subtitle_id) REFERENCES subtitle_language_table(id)
            )
            ''')

            # Create end_video_table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS end_video_table (
                video_id INTEGER NOT NULL,
                end_video_1_id INTEGER DEFAULT NULL,
                end_video_2_id INTEGER DEFAULT NULL,
                FOREIGN KEY (video_id) REFERENCES video_table(id),
                FOREIGN KEY (end_video_1_id) REFERENCES video_table(id),
                FOREIGN KEY (end_video_2_id) REFERENCES video_table(id)
            )
            ''')

if __name__ == "__main__":
    database_execution()
