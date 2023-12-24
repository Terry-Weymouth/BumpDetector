"""
Build or rebuild database, including track data, and added processed data.
Data files are *_Cleaned.txt in the top level directory ./data
Database table and index SQL statements are in ./src/sql/init_track_tables.sql
    Note: the above will also drop, then create the track-related tables
In addition to loading the data this program also
    sets the nearest road ID and distance in the database
"""
import psycopg2
from src.config.get_config import get_database_access
from src.lib.load_gps_tracks import load_track_data

global connection, cursor


def apply_sql_file(file_path):
    global connection, cursor
    print("applying to database", file_path)
    try:
        # Read SQL statements from the file
        with open(file_path, 'r') as file:
            sql_statements = file.read()

        # Split SQL statements using the semicolon as a delimiter
        statements = sql_statements.split(';')

        # Execute each SQL statement
        for statement in statements:
            if statement and statement.strip():  # Skip empty statements
                cursor.execute(statement)

        # Commit the changes
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing SQL statements: {error}")


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def main():
    global connection, cursor
    make_connection()  # if successful - sets connection, cursor
    if connection:
        apply_sql_file("src/sql/remove_rebuild_track_tables.sql")
        load_track_data(cursor, connection)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
