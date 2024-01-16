import psycopg2
from src.config.get_config import get_database_access
from src.config.get_config import get_mapgl_access


header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"
output_filepath = "mapboxgl_explore_tracks_with_roads.html"

"""
select ST_AsGeoJSON(ST_Transform(way,4326))
    from map_matching_roads as roads
    join planet_osm_line as osm
        on (roads.osm_id=osm.osm_id)
where ST_Overlaps(ST_Transform(way,4326),
    ST_MakeEnvelope(-83.145066509, 42.493609926, -83.143829920, 42.494761427, 4326))
"""


def get_road_geom():
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
        select ST_AsGeoJSON(ST_Transform(way,4326)), osm_id
        from planet_osm_line
        where
            100 > ST_Distance(way,(ST_Transform
                (ST_GeomFromText('POINT(-83.14448238874682 42.49406222012129)',4326), 3857)))
            and name <> ''
            and osm_id > 0
        order by osm_id
        """
        cursor.execute(query)
        record = cursor.fetchall()
        print(f"Found {len(record)} roads")
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return record


def add_road_geom(out_file, geom_list):
    # loader header
    out_file.write("map.on('style.load', () => {\n")
    # loader content
    color_list = ['black', 'red', 'green', 'blue', 'orange']
    for i in range(0, len(geom_list)):
        color = color_list[i % len(color_list)]
        osm_id = geom_list[i][1]
        print(i, color, osm_id)
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
                    'line-color': '{color}',
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
            center: [-83.144588,42.4934077],
            zoom: 16.5,  
        });
        map.on('style.load', function() {
            map.on('click', function(e) {
                var coordinates = e.lngLat;
                new mapboxgl.Popup()
                   .setLngLat(coordinates)
                   .setHTML('you clicked here: <br/>' + coordinates)
                   .addTo(map);
            });
        });
        """
    )


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def add_access_token(out_file):
    token = get_mapgl_access()['token']
    out_file.write("\t\tmapboxgl.accessToken = '{}'\n".format(token))


def get_track_geom():
    connection = None
    cursor = None
    point_list = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
            select long, lat
            from bicycle_data
            where track_id = 1
                and 300 > ST_Distance(
                    ST_Transform(long_lat_original, 3857),
                    ST_Transform(ST_GeomFromText('POINT(-83.14448238874682 42.49406222012129)',4326), 3857)
                    )
            order by id
        """
        cursor.execute(query)
        point_list = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return point_list


def add_track_geom(out_file, track_data):
    track_color = 'red'
    points_var_name = "points_long_lat"

    out_file.write("let {} = [];\n".format(points_var_name))

    for point in track_data:
        long = point[0]
        lat = point[1]
        out_file.write(f"{points_var_name}.push([{long},{lat}]);\n")

    out_file.write(f"""
        // Add markers for each point (marker in new DOM dev)
        {points_var_name}.forEach(function(point) {{
            var el = document.createElement('div');
            el.className = 'marker';
            el.style.background = '{track_color}';
            new mapboxgl.Marker(el)
              .setLngLat(point)
              .addTo(map);
        }});
    """)


def main():
    track_geom = get_track_geom()
    road_geom = get_road_geom()
    output = output_filepath
    print(f"Found {len(track_geom)} track points")
    print(track_geom[0], track_geom[-1])
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file)
        add_road_geom(out_file, road_geom)
        add_track_geom(out_file, track_geom)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
