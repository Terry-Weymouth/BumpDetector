"""
Build or rebuild database, including track data, and added processed data.
Data files are *_Cleaned.txt in the top level directory './data'.
Data files are not reloaded if they are already in the database;
    to override this behavior use the --force flag (see argparse below)
Database table and index SQL statements are in ./src/sql/init_track_tables.sql
    Note: the above will also drop, then create the track-related tables
In addition to loading the data this program also
    sets the nearest road ID and distance in the database
"""
import psycopg2
import argparse
from src.config.get_config import get_database_access
from src.lib.load_gps_tracks import load_track_data
from src.lib.get_files_for_loading_tracks import get_trace_file_paths

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


def main(rebuild):
    global connection, cursor
    make_connection()  # if successful - sets connection, cursor
    if connection:
        file_path_list = get_trace_file_paths(connection, cursor, rebuild)
        print(f"load from files: {file_path_list}")
        if rebuild:
            apply_sql_file("src/sql/remove_rebuild_track_tables.sql")
        if file_path_list:
            load_track_data(cursor, connection, file_path_list)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert raw GPS/Bump data to internal; remove useless records.')
    parser.add_argument('--force', action='store_true', help='completely rebuild database using all files')
    args = parser.parse_args()
    force_rebuild = args.force
    print(f"force_rebuild = {force_rebuild}")
    main(force_rebuild)
