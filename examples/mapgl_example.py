import psycopg2
from src.config.get_config import get_database_access
from src.config.get_config import get_mapgl_access


header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"


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


def add_geom(out_file, geom_list):
    for i in range(0, len(geom_list)):
        geom = geom_list[i][0]
        name = "geom{}".format(i)

        out_file.write("\tvar {} = {};\n".format(name, geom))
        out_file.write("\tL.geoJSON({}).addTo(mymap);\n".format(name))


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def add_access_token(out_file):
    token = get_mapgl_access()['token']
    out_file.write("\t\tmapboxgl.accessToken = '{}'\n".format(token))


def main():
    road_geom = connect_and_query()
    output = "mapgl_example.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_geom(out_file, road_geom)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
