import os
import sqlite3

def get_db_connection():
  """Connects to the YouTube database in the mounted volume."""
  # Get the path to the database file within the container
  database_path = os.path.join('./output/database', 'youtube.db')

  # Establish the connection using the full path
  conn = sqlite3.connect(database_path)
  conn.row_factory = sqlite3.Row
  return conn