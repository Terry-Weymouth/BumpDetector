import time as clock
import numpy as np
from datetime import datetime
from psycopg2 import sql
from src.lib.progress_bar import print_progress, clear_progress

global connection, cursor, max_d


def load_track_data(cur, con, file_path_list):
    global connection, cursor, max_d
    connection = con
    cursor = cur
    max_d = 0

    for file_path in file_path_list:
        start_time = clock.time()
        print("loading data from", file_path)
        point_list = create_point_list(file_path)
        track_index = add_new_track(file_path)
        add_points(track_index, point_list)
        update_with_geometry(track_index)
        print(f"initial data loaded; update with distance to road, for track {track_index}")

        limits = get_id_limits(track_index)
        results_list = []
        for point_id in range(limits[0], limits[1] + 1):
            results = get_nearest_road_and_distance(track_index, point_id)
            if results:
                results_list.append(results)
            print_progress(point_id, limits[0], limits[1])
        add_road_and_distance(results_list)
        clear_progress(f"distance to road added for track {track_index}")
        record_max_distance(track_index, max_d)
        secs = int(clock.time() - start_time + 0.49)
        num_records = limits[1] - limits[0] + 1
        print(f"Added track {track_index} ({num_records} records) in {secs} secs")


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
    query = (sql.SQL("insert into {}({},{}) values (%s, %s) returning track_id ")
             .format(sql.Identifier('bicycle_track'),
                     sql.Identifier('file_path'),
                     sql.Identifier('time')))
    time_of_insert = datetime.now()
    print(query, source_filename, time_of_insert)
    cursor.execute(query,[source_filename, time_of_insert])
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


def update_with_geometry(track_index):
    query = sql.SQL("UPDATE bicycle_data SET long_lat_original"
                    + "= ST_SetSRID(ST_MakePoint(long, lat), 4326)::geometry "
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
        print(f"No distance results for track_id = {track_id} with point_id = {point_id}")
    return results


def add_road_and_distance(results_list):
    global cursor, connection
    for item in results_list:
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
