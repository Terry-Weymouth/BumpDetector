import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access
from src.config.get_config import get_mapgl_access

global connection, cursor

header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"


def connect_and_query():
    global connection
    global cursor
    road_pairs = []
    try:
        make_connection()
        query_str = """
        select one.osm_id, two.osm_id
        from
            planet_osm_line as one, planet_osm_line as two
        where one.osm_id < two.osm_id
            and one.osm_id in (select distinct nearest_road_id from bicycle_data)
            and two.osm_id in (select distinct nearest_road_id from bicycle_data)
            and ST_Distance(one.way, two.way) = 0
        order by one.osm_id, two.osm_id
        """
        query = sql.SQL(query_str)
        # noinspection PyUnresolvedReferences
        cursor.execute(query)
        # noinspection PyUnresolvedReferences
        road_pairs = cursor.fetchall()
        road_list = []
        for p in road_pairs:
            for road in p:
                if road not in road_list:
                    road_list.append(road)
        road_list_string = "(" + ','.join([str(r) for r in road_list]) + ")"
        print(road_list_string)
        query_str = f"""
        select ST_AsGeoJSON(ST_Transform(way,4326))
            from planet_osm_line
            where osm_id in {road_list_string}
        """
        query = sql.SQL(query_str)
        # noinspection PyUnresolvedReferences
        cursor.execute(query)
        # noinspection PyUnresolvedReferences
        roads = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return roads


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def add_geom(out_file, geom_list):
    # loader header
    out_file.write("map.on('style.load', () => {\n")
    # loader content
    for i in range(0, len(geom_list)):
        geom_item = geom_list[i][0]
        geom_name = "geom{}".format(i)
        map_item_name = "track{}".format(i)
        doc_string = f"""
            var {geom_name} = {geom_item};
            map.addSource('{map_item_name}', {{
                type: 'geojson',
                data: {{
                    'type': 'Feature',
                    'properties': {{}},
                    'geometry': {geom_name} }}
            }});
            map.addLayer({{
                id: '{map_item_name}',
                type: 'line',
                source: '{map_item_name}',
                paint: {{
                    'line-color': '#888',
                    'line-width': 3
                }}
            }});
        """
        out_file.write(doc_string)
    # loader footer
    out_file.write("});\n")


def add_map_base(out_file):
    out_file.write(
        """\t\tconst map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [-83.1592,42.4939],
            zoom: 16.5,
        });
        """
    )


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def add_access_token(out_file):
    token = get_mapgl_access()['token']
    out_file.write("\t\tmapboxgl.accessToken = '{}'\n".format(token))


def main():
    road_geom = connect_and_query()
    print(len(road_geom))
    output = "mapgl_example.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file)
        add_geom(out_file, road_geom)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
