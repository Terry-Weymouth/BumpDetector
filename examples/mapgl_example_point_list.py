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
        geom = "ST_AsGeoJSON(ST_Transform(long_lat_original,4326))"
        table = "bicycle_data"
        where = "track_id=1 order by id"
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
    track_geom = connect_and_query()
    print(len(track_geom))
    output = "mapgl_example.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file)
        add_geom(out_file, track_geom)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()

"""
latLongs0 = [
    [42.4940865, -83.1593145], [42.4940735, -83.159352333], [42.494052667, -83.159366333],
    [42.494023333, -83.159373333], [42.4939875, -83.159380833], [42.4939555, -83.1593875], [42.4939225, -83.159391833],
    [42.493887667, -83.159389667], [42.493849667, -83.159386333], [42.493809333, -83.1593885],
    [42.493769833, -83.159387167], [42.493727833, -83.159382833], [42.493687667, -83.1593825],
    [42.493645667, -83.159383667], [42.493603167, -83.159385667], [42.493561667, -83.159384167],
    [42.493520333, -83.159380833], [42.493485, -83.1593685], [42.493453667, -83.159345],
    [42.49343, -83.159312333], [42.493403167, -83.159269333], [42.4933785, -83.159225833],
    [42.493365, -83.159174], [42.493355333, -83.159105167], [42.493352167, -83.159034167],
    [42.4933525, -83.158964833], [42.493352667, -83.158892], [42.4933565, -83.158809333],
    [42.493361333, -83.1587215], [42.4933675, -83.158634167], [42.493371833, -83.158546333],
    [42.493378333, -83.158464167], [42.493382167, -83.158377], [42.493379333, -83.158287333],
    [42.493372, -83.158195833], [42.493368167, -83.1581065], [42.493366667, -83.1580155],
    [42.4933675, -83.157922833], [42.493367833, -83.157833167], [42.493370667, -83.157744667],
    [42.493373333, -83.157655333], [42.493376833, -83.157567333], [42.493381333, -83.15748],
    [42.493386333, -83.157394], [42.493388333, -83.157309167], [42.493392, -83.157222],
    [42.493395667, -83.157136], [42.4933975, -83.157052167], [42.493401, -83.1569725],
]

"""

"""
[('{"type":"LineString","coordinates":[[-83.1590104,42.499099601],[-83.1590112,42.499171101],[-83.1590466,42.500186201],[-83.1590488,42.500252101],[-83.1590516,42.500322401],[-83.1590853,42.501180001],[-83.1590857,42.501244901],[-83.1590895,42.501308701],[-83.1591236,42.502278901]]}',), ('{"type":"LineString","coordinates":[[-83.1593601,42.493396501],[-83.1593622,42.493476701],[-83.159365,42.493549201],[-83.1593764,42.493839901],[-83.1593806,42.493947101],[-83.1593854,42.494069801],[-83.159388,42.494136001],[-83.1593939,42.494330301],[-83.1593963,42.494407901],[-83.1594027,42.494619001],[-83.1594065,42.494742301],[-83.159408,42.494792001],[-83.1594142,42.494938101],[-83.1594188,42.495045001],[-83.1594202,42.495076001],[-83.159435,42.495423001],[-83.1594803,42.496510701],[-83.1594957,42.496881601],[-83.1595564,42.496956901]]}',), ('{"type":"LineString","coordinates":[[-83.1612014,42.492161001],[-83.1610072,42.492252101],[-83.1608319,42.492334401],[-83.160822,42.492339001],[-83.160751,42.492397001],[-83.160471,42.492740001],[-83.1602164,42.493050801],[-83.160142,42.493146001],[-83.1598722,42.493525701],[-83.159836,42.493577001]]}',), ('{"type":"LineString","coordinates":[[-83.1595564,42.496956901],[-83.1596092,42.497040301],[-83.159614,42.497172001],[-83.1596751,42.498974801],[-83.1596801,42.499034101]]}',)]
"""