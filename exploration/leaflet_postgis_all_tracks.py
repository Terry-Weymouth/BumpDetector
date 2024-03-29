import argparse
import os
import psycopg2
from psycopg2 import sql

header_filepath = "../leaflet/leaflet_header.txt"
footer_filepath = "../leaflet/leaflet_footer.txt"

connection = None
cursor = None

max_coded_value = 0.0
color_list = [
    (255, 0, 0),
    (255, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (178, 76, 76),
    (153, 102, 102),
    (127, 127, 127),
    (102, 153, 153),
    (76, 178, 178),
    (51, 204, 240),
    (25, 229, 229),
    (0, 255, 255)
]


def make_connection():
    global connection, cursor
    try:
        connection = psycopg2.connect(user="weymouth",
                                      password="",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="Detroit")
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)


def print_bounding_box(out_file):
    bound_upper = 42.494433
    bound_lower = 42.493725
    bound_left = -83.159279
    bound_right = -83.158586

    out_file.write("\t{}\n".format("var polygon = L.polygon(["))
    out_file.write("\t\t[{}, {}], ".format(bound_upper,bound_left))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_right))
    out_file.write("\t\t[{}, {}], ".format(bound_lower,bound_right))
    out_file.write("\t\t[{}, {}] ".format(bound_lower, bound_left))
    out_file.write("\t{}\n".format("]).addTo(mymap);"))


def add_geom(out_file, geom_list):
    for i in range(0, len(geom_list)):
        geom = geom_list[i][0]
        name = "geom{}".format(i)
        out_file.write("\tvar {} = {};\n".format(name, geom))
        out_file.write("\tL.geoJSON({}).addTo(mymap);\n".format(name))


def create_point_list():
    global cursor, max_coded_value
    query_str = "select lat, long, track_id from bicycle_data order by track_id, id;"
    # query_str = "select ST_Y(long_lat_remapped::geometry) as lat, " \
    #            + "ST_X(long_lat_remapped::geometry) as long, " \
    #            + "nearest_road_distance from bicycle_data order by id;"
    query = sql.SQL(query_str)
    cursor.execute(query)
    query_results = cursor.fetchall()
    max_coded_value = 0
    results = []
    for r in query_results:
        value = r[2]
        max_coded_value = max(max_coded_value, value)
        results.append(list(r))
    max_coded_value = 9.0
    return results


def segment_point_list(annotated_point_list):
    track_id = annotated_point_list[0][2]
    segment_index = (track_id -1) % 11
    cache = []
    results = []
    for record in annotated_point_list:
        track_id = record[2]
        color_index = (track_id -1) % 11
        if not color_index == segment_index:
            cache.append(record)
            results.append([segment_index, cache])
            segment_index = color_index
            cache = []
        cache.append(record)
    results.append([segment_index, cache])
    return results


def make_point_list():
    return segment_point_list(create_point_list())


def add_point_list(out_file, segmented_point_list):
    global color_list
    count = 0
    for segment in segmented_point_list:
        color = color_list[segment[0]]
        r, g, b = color
        var_name = "latLongs{}".format(count)
        res_name = "ployline{}".format(count)
        count += 1
        out_file.write("\tvar {} = [\n".format(var_name))
        for record in segment[1]:
            lat = record[0]
            long = record[1]
            out_file.write("\t\t[{}, {}],\n".format(lat, long))
        out_file.write("\t];\n")
        out_file.write("\t{} = L.polyline({}, {}color: 'rgb({},{},{})'{} ).addTo(mymap);\n".format(
            res_name, var_name, "{", r, g, b, "}"))


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def main():
    global connection, cursor
    make_connection()
    if cursor:
        point_list = make_point_list()
        output = "All_tracks_probe.html"
        if point_list:
            with open(output, "w") as out_file:
                copy_path_content(header_filepath, out_file)
                print_bounding_box(out_file)
                add_point_list(out_file, point_list)
                copy_path_content(footer_filepath, out_file)
    if cursor:
        cursor.close()
    if connection:
        connection.close()


if __name__ == "__main__":
    main()
