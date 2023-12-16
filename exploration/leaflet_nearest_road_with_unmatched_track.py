import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

header_filepath = "leaflet/leaflet_header.txt"
footer_filepath = "leaflet/leaflet_footer.txt"

connection = None
cursor = None

max_coded_value = 0.0
color_list = [
    (255, 0, 0),
    (229, 25, 25),
    (204, 51, 51),
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
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def query_ways():
    global cursor

    record = None
    try:
        # noinspection PyUnresolvedReferences
        cursor = connection.cursor()
        geom = "ST_AsGeoJSON(ST_Transform(way,4326))"
        table1 = "(select distinct nearest_road_id as id from bicycle_data) as road"
        table2 = "planet_osm_line as osm"
        join_on = "(road.id=osm.osm_id)"
        query = "select {} from {} join {} on {};".format(geom, table1, table2, join_on)
        cursor.execute(query)
        record = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    return record


def print_bounding_box(out_file):
    bound_upper = 42.494433
    bound_lower = 42.493725
    bound_left = -83.159279
    bound_right = -83.158586

    out_file.write("\t{}\n".format("var polygon = L.polygon(["))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_left))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_right))
    out_file.write("\t\t[{}, {}], ".format(bound_lower, bound_right))
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
    query_str = "select lat, long, nearest_road_distance from bicycle_data order by id;"
    # query_str = "select ST_Y(long_lat_remapped::geometry) as lat, " \
    #            + "ST_X(long_lat_remapped::geometry) as long, " \
    #            + "nearest_road_distance from bicycle_data order by id;"
    query = sql.SQL(query_str)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    query_results = cursor.fetchall()
    max_coded_value = 0
    results = []
    for r in query_results:
        value = r[2]
        max_coded_value = max(max_coded_value, value)
        results.append(list(r))
    max_coded_value = 9.0
    return results


def annotate_point_list(point_list):
    global max_coded_value
    index_limit = 11
    results = []
    for record in point_list:
        distance = record[2]
        index = int((distance/max_coded_value) * float(index_limit))
        if index >= index_limit:
            index = index_limit - 1
        record.append(index)
        results.append(record)
    return results


def segment_point_list(annotated_point_list):
    segment_index = annotated_point_list[0][3]
    cache = []
    results = []
    for record in annotated_point_list:
        color_index = record[3]
        if not color_index == segment_index:
            cache.append(record)
            results.append([segment_index, cache])
            segment_index = color_index
            cache = []
        cache.append(record)
#    if len(cache) == 1:
#        cache.append(cache[0])
    results.append([segment_index, cache])
    return results


def make_point_list():
    return segment_point_list(annotate_point_list(create_point_list()))


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
        road_geom = query_ways()
        point_list = make_point_list()
        output = "PostGIS_probe.html"
        if point_list and road_geom:
            with open(output, "w") as out_file:
                copy_path_content(header_filepath, out_file)
                print_bounding_box(out_file)
                add_geom(out_file, road_geom)
                add_point_list(out_file, point_list)
                copy_path_content(footer_filepath, out_file)
    if cursor:
        # noinspection PyUnresolvedReferences
        cursor.close()
    if connection:
        # noinspection PyUnresolvedReferences
        connection.close()


if __name__ == "__main__":
    main()
