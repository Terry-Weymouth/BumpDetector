import psycopg2
from src.config.get_config import get_database_access
from src.config.get_config import get_mapgl_access

header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"


def tracks_connect_and_query(track_id_list):
    connection = None
    cursor = None
    track_data = []
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        for track_id in track_id_list:
            query = f"""
                select long, lat, ST_X(long_lat_remapped), ST_Y(long_lat_remapped)
                from bicycle_data a join map_matching_results b on a.id=b.data_id
                where track_id={track_id}
                order by a.id
            """
            cursor.execute(query)
            point_list = cursor.fetchall()
            track_data.append((track_id, point_list))
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return track_data


def tracks_add_geom(out_file, track_data):
    index = 0
    track_colors = ['orange', 'red']
    for track_desc in track_data:
        track_id = track_desc[0]
        track_points = track_desc[1]
        print(f"geom for track {track_id}")
        for sub_track in range(len(track_colors)):
            track_color = track_colors[sub_track]
            points_var_name = f"points_long_lat_{index}"
            index = index + 1

            out_file.write("//for track id = {}, color = {}\n".format(track_id, track_color))
            out_file.write("let {} = [];\n".format(points_var_name))

            for point in track_points:
                offset = 2 * sub_track
                long = point[0 + offset]
                lat = point[1 + offset]
                out_file.write('{}.push([{},{}]);\n'.format(points_var_name, long, lat))

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


def matched_roads_connect_and_query():
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
            select ST_AsGeoJSON(ST_Transform(way,4326))
                from map_matching_roads as roads
                join planet_osm_line as osm
                    on (roads.osm_id=osm.osm_id)
        """
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


def get_track_id_list():
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
        select track_id 
            from bicycle_track
        """
        cursor.execute(query)
        record = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return [x[0] for x in record]


def tracks_add_as_line(out_file, track_data_line):
    pass


def roads_add_geom(out_file, geom_list):
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
                    'line-color': '#555',
                    'line-width': 2
                }}
            }});
        """
        out_file.write(doc_string)
    # loader footer
    out_file.write("});\n")


def compute_all_track_data_centroid(track_data):
    long_centroid = 0.0
    lat_centroid = 0.0
    n = 0
    for track in track_data:
        position_data = track[1]
        for position in position_data:
            (long, lat, _, _) = position
            long_centroid = (long_centroid*n + long)/(n + 1)
            lat_centroid = (lat_centroid*n + lat)/(n + 1)
            n = n + 1
    return long_centroid, lat_centroid


def add_map_base(out_file, track_data):
    (long, lat) = compute_all_track_data_centroid(track_data)
    out_file.write(
        f"""\t\tconst map = new mapboxgl.Map({{
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [{long},{lat}],
            zoom: 13,
        }});
        """
    )


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def add_access_token(out_file):
    token = get_mapgl_access()['token']
    out_file.write("\t\tmapboxgl.accessToken = '{}'\n".format(token))


def make_line_from_matched_track(track_id):
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
            SELECT ST_AsGeoJSON( ST_MakeLine( ARRAY (
                select long_lat_remapped
                from map_matching_results r join bicycle_data d on r.data_id = d.id
                where d.track_id = 2)) )
        """
        cursor.execute(query)
        record = cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
    return record[0][0]


def main():
    all_track_id = get_track_id_list()
    print(all_track_id)
    track_data = tracks_connect_and_query(all_track_id)
    track_data_line = make_line_from_matched_track(2)
    print(track_data[1][1][0:4])
    print(track_data_line)
    exit(0)
    road_data = matched_roads_connect_and_query()
    output = "mapboxgl_roads_viterbi_tracks.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file, track_data)
        roads_add_geom(out_file, road_data)
        # tracks_add_geom(out_file, track_data)
        tracks_add_as_line(out_file, track_data)
        copy_path_content(footer_filepath, out_file)
    print("Done: {} roads, {} tracks".format(len(road_data), len(track_data)))


if __name__ == "__main__":
    main()
