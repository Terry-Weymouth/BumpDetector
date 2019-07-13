import argparse
import numpy as np
import psycopg2
from psycopg2 import sql
from datetime import datetime

connection = None
cursor = None


def make_connection():
    global connection, cursor
    connection = psycopg2.connect(user="weymouth",
                                  password="",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="Detroit")
    cursor = connection.cursor()


def create_point_list(file_path):
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    table = np.array([x.split(",") for x in content])
    g1 = table[:, 0].astype(np.float)
    g2 = table[:, 1].astype(np.float)
    g3 = table[:, 2].astype(np.float)
    g4 = table[:, 3].astype(np.float)
    g5 = table[:, 4].astype(np.float)
    g6 = table[:, 5].astype(np.float)

    time = table[:, 6].astype(np.datetime64)

    lat = table[:, 7].astype(np.float)
    long = table[:, 8].astype(np.float)
    alt = table[:, 9].astype(np.float)
    speed = table[:, 10].astype(np.float)

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
                           time[i], lat[i], long[i], alt[i], speed[i], delta_time[i] ])
    return point_list


def add_new_track(source_filename):
    cursor.execute(sql.SQL("insert into {}({},{}) values (%s, %s) returning track_id ")\
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


def main():
    parser = argparse.ArgumentParser(description='Write cleaned GPS/Bump data to Detroit database.')
    parser.add_argument('--source', type=str, help='Require path to cleaned source data')
    args = parser.parse_args()
    source = args.source
    if not source:
        print("**********************************")
        print("The --source argument is required.")
        print("**********************************")
        parser.print_help()
        exit(-1)
    print("Using source = " + source)

    global connection, cursor
    try:
        make_connection()
        point_list = create_point_list(source)
        track_index = add_new_track(source)
        add_points(track_index, point_list)
        update_with_geography(track_index)
        print("Added track: {}".format(track_index))
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #closing database connection.
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
