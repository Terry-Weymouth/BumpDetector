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


"""
        map.on('style.load', () => {
            var geom0 = {"type":"LineString",
                    "coordinates":[[-83.1590104,42.499099601],[-83.1590112,42.499171101],[-83.1590466,42.500186201],[-83.1590488,42.500252101],[-83.1590516,42.500322401],[-83.1590853,42.501180001],[-83.1590857,42.501244901],[-83.1590895,42.501308701],[-83.1591236,42.502278901]]
            };
            map.addSource('route', {
                type: 'geojson',
                data: {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': geom0 }
            });
            map.addLayer({
                id: 'route',
                type: 'line',
                source: 'route',
                paint: {
                    'line-color': '#888',
                    'line-width': 3
                }
            });
        });
"""


def add_geom(out_file, geom_list):
    # loader header
    out_file.write("map.on('style.load', () => {\n")
    # loader content
    for i in range(0, len(geom_list)):
        print("loop", i)
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
