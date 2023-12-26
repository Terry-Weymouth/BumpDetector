import psycopg2
from src.config.get_config import get_database_access
from src.config.get_config import get_mapgl_access


header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"


def connect_and_query():
    connection = None
    cursor = None
    track_data = []
    try:
        track_color_array = ['red', 'blue', 'green', 'orange', 'yellow', 'cyan']
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = "select track_id from bicycle_track order by track_id"
        cursor.execute(query)
        tracks = cursor.fetchall()
        for track_record in tracks:
            track_id = track_record[0]
            track_color = track_color_array[(track_id - 1) % len(track_color_array)]
            query = "select long, lat from bicycle_data where track_id={} order by id".format(track_id)
            cursor.execute(query)
            point_list = cursor.fetchall()
            track_data.append((track_id, track_color, point_list))
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if cursor:
            cursor.close()
        if connection:
            connection.close()
    return track_data


def add_geom(out_file, track_data):
    index = 0
    for track_desc in track_data:
        points_var_name = "points_long_lat{}".format(index)
        index = index + 1
        track_id = track_desc[0]
        track_color = track_desc[1]
        track_points = track_desc[2]

        out_file.write("//for track id = {}, color = {}\n".format(track_id, track_color))
        out_file.write("let {} = [];\n".format(points_var_name))

        for point in track_points:
            out_file.write('{}.push([{},{}]);\n'.format(points_var_name, point[0], point[1]))

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


def compute_all_track_data_centroid(track_data):
    long_centroid = 0.0
    lat_centroid = 0.0
    n = 0
    for track in track_data:
        position_data = track[2]
        for position in position_data:
            (long, lat) = position
            long_centroid = (long_centroid*n + long)/(n + 1)
            lat_centroid = (lat_centroid*n + lat)/(n + 1)
            n = n + 1
    return long_centroid, lat_centroid


def add_map_base(out_file, track_data):
    (long, lat) = compute_all_track_data_centroid(track_data)
    print(long, lat)
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


def main():
    track_data = connect_and_query()
    output = "mapboxgl_chatgpt_example.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file, track_data)
        add_geom(out_file, track_data)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
