"""
Build or rebuild database, including track data, and added processed data.
Data files are *_Cleaned.txt in the top level directory ./data
Database table and index SQL statements are in ./src/sql/init_track_tables.sql
    Note: the above will also drop, then create the track-related tables
In addition to loading the data this program also
    sets the nearest road ID and distance in the database
"""
import os
import fnmatch
import numpy as np
from datetime import datetime
import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

global connection, cursor, max_d


def find_files(directory, pattern):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            file_list.append(os.path.join(root, filename))
    return file_list


def load_track_data():
    directory_path = "./data"  # Change this to the desired directory path
    pattern = "*_Cleaned.txt"
    matching_files = find_files(directory_path, pattern)
    for file_path in matching_files:
        print("loading data from", file_path)
        point_list = create_point_list(file_path)
        track_index = add_new_track(file_path)
        add_points(track_index, point_list)
        update_with_geography(track_index)
        print("Added track: {}".format(track_index))
        limits = get_id_limits(track_index)
        print(limits)
        results_list = []
        for point_id in range(limits[0], limits[1] + 1):
            results = get_nearest_road_and_distance(track_index, point_id)
            if results:
                results_list.append(results)
        add_road_and_distance(results_list)
        record_max_distance(track_index, max_d)


def create_point_list(file_path):
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    table = np.array([x.split(",") for x in content])
    g1 = table[:, 0].astype(float)
    g2 = table[:, 1].astype(float)
    g3 = table[:, 2].astype(float)
    g4 = table[:, 3].astype(float)
    g5 = table[:, 4].astype(float)
    g6 = table[:, 5].astype(float)

    time = table[:, 6].astype(np.datetime64)

    lat = table[:, 7].astype(float)
    long = table[:, 8].astype(float)
    alt = table[:, 9].astype(float)
    speed = table[:, 10].astype(float)

    max_g = np.maximum(g1, g2)
    max_g = np.maximum(max_g, g3)
    max_g = np.maximum(max_g, g4)
    max_g = np.maximum(max_g, g5)
    max_g = np.maximum(max_g, g6)

    base_time = time[0]
    delta_time = [(probe - base_time).item().total_seconds() for probe in time]

    point_list = []
    for i in range(len(max_g)):
        point_list.append([g1[i], g2[i], g3[i], g4[i], g5[i], g6[i], max_g[i],
                           time[i], lat[i], long[i], alt[i], speed[i], delta_time[i]])
    return point_list


def add_new_track(source_filename):
    cursor.execute(sql.SQL("insert into {}({},{}) values (%s, %s) returning track_id ")
                   .format(sql.Identifier('bicycle_track'),
                           sql.Identifier('file_path'),
                           sql.Identifier('time')),
                   [source_filename, datetime.now()])
    connection.commit()
    track_index = cursor.fetchone()[0]
    return track_index


def add_points(track_index, point_list):
    field_list = [
        "track_id",
        "g1", "g2", "g3", "g4", "g5", "g6", "gmax",
        "time", "lat", "long", "alt", "speed", "delta_time"]
    fields = sql.SQL(', ').join((sql.Identifier(x) for x in field_list))
    template = sql.SQL(', ').join(sql.Placeholder() * len(field_list))
    query = sql.SQL("insert into {}({}) values ({}) returning track_id ") \
        .format(sql.Identifier('bicycle_data'), fields, template)

    for point in point_list:
        point.insert(0, track_index)
        # convert numpy.datetime64 to datetime.datetime
        point[8] = point[8].tolist()
        cursor.execute(query, point)
    connection.commit()


def update_with_geography(track_index):
    query = sql.SQL("UPDATE bicycle_data SET long_lat_original "
                    + "= ST_SetSRID(ST_MakePoint(long, lat), 4326)::geography "
                    + "where track_id={};"
                    .format(track_index))
    cursor.execute(query)
    connection.commit()


def get_id_limits(track_id):
    query_str = "select min(id), max(id) from bicycle_data where track_id={};"
    query_str = query_str.format(track_id)
    query = sql.SQL(query_str)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchone()
    return results


def get_nearest_road_and_distance(track_id, point_id):
    global cursor, max_d
    query_str = "select track.id, osm.osm_id, osm.name, osm.highway, "\
        + "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) "\
        + "from bicycle_data as track, planet_osm_line as osm "\
        + "where track.track_id={} and track.id={} and "\
        + "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) < 70.0 " \
        + "and highway is not null " \
        + "and not (highway in ('footway', 'tertiary_link', 'motorway'))" \
        + "order by st_distance limit 1;"
    query_str = query_str.format(track_id, point_id)
    query = sql.SQL(query_str)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchone()
    if results:
        d = results[4]
        if d > max_d:
            max_d = d
    else:
        print("Missing id =", id)
    return results


def add_road_and_distance(results_list):
    global cursor, connection
    for item in results_list:
        print(item)
        point_id = item[0]
        way_id = item[1]
        distance = item[4]
        query = sql.SQL("UPDATE bicycle_data "
                        + "SET nearest_road_id=%s, "
                        + "nearest_road_distance=%s "
                        + "where id={};"
                        .format(point_id))
        # noinspection PyUnresolvedReferences
        cursor.execute(query, (way_id, distance))
    # noinspection PyUnresolvedReferences
    connection.commit()


def record_max_distance(track_id, d):
    query = sql.SQL("UPDATE bicycle_track "
                    + "SET max_distance=%s "
                    + "where track_id={};"
                    .format(track_id))
    # noinspection PyUnresolvedReferences
    cursor.execute(query, (d,))
    # noinspection PyUnresolvedReferences
    connection.commit()


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
                print(statement)
                cursor.execute(statement)

        # Commit the changes
        connection.commit()
        print("SQL statements executed successfully.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error executing SQL statements: {error}")


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def main():
    global connection, cursor, max_d
    max_d = 0
    make_connection()  # if successful - sets connection, cursor
    if connection:
        apply_sql_file("src/sql/remove_rebuild_track_tables.sql")
        load_track_data()
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
