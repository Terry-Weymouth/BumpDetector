import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

connection = None
cursor = None
max_d = 0


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def get_id_limits(track_id):
    query_str = "select min(id), max(id) from bicycle_data where track_id={};"
    query_str = query_str.format(track_id)
    query = sql.SQL(query_str)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchone()
    return results


def probe(track_id, point_id):
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


def update_records(results_list):
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
    global cursor, connection
    query = sql.SQL("UPDATE bicycle_track "
                    + "SET max_distance=%s "
                    + "where track_id={};"
                    .format(track_id))
    # noinspection PyUnresolvedReferences
    cursor.execute(query, (d,))
    # noinspection PyUnresolvedReferences
    connection.commit()


def main():
    # TODO: process all tracks that have no max distance
    global connection, cursor, max_d
    track_index = 1
    try:
        make_connection()
        limits = get_id_limits(track_index)
        print(limits)
        results_list = []
        for point_id in range(limits[0], limits[1] + 1):
            results = probe(track_index, point_id)
            if results:
                results_list.append(results)
        update_records(results_list)
        record_max_distance(track_index, max_d)
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            # noinspection PyUnresolvedReferences
            cursor.close()
            # noinspection PyUnresolvedReferences
            connection.close()


if __name__ == "__main__":
    main()
