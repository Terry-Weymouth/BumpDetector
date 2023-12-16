import psycopg2
from src.config.get_config import get_database_access


header_filepath = "leaflet/leaflet_header.txt"
footer_filepath = "leaflet/leaflet_footer.txt"


def connect_and_query():
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        geom = "ST_AsGeoJSON(ST_Transform(way,4326))"
        table = "planet_osm_line"
        where = "name='Forestdale Road'"
        query = "select {} as g from {} where {};".format(geom, table, where)
        cursor.execute(query)
        record = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
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


def close_enough(a, b):
    epsilon = 0.00000001
    return abs(a - b) < epsilon


def add_geom(out_file, geom_list):
    for i in range(0, len(geom_list)):
        geom = geom_list[i][0]
        name = "geom{}".format(i)
        out_file.write("\tvar {} = {};\n".format(name, geom))
        out_file.write("\tL.geoJSON({}).addTo(mymap);\n".format(name))


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def main():
    road_geom = connect_and_query()
    output = "PostGIS_probe.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        print_bounding_box(out_file)
        add_geom(out_file, road_geom)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
