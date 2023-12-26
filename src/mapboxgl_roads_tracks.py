from src.config.get_config import get_mapgl_access
import src.lib.map_adjecent_roads as roads
import src.lib.map_raw_tracks as tracks

header_filepath = "leaflet/mapgl_header.txt"
footer_filepath = "leaflet/mapgl_footer.txt"


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
    track_data = tracks.connect_and_query()
    road_data = roads.connect_and_query()
    output = "mapboxgl_roads_tracks.html"
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        add_access_token(out_file)
        add_map_base(out_file, track_data)
        roads.add_geom(out_file, road_data)
        tracks.add_geom(out_file, track_data)
        copy_path_content(footer_filepath, out_file)
    print("Done: {} roads, {} tracks".format(len(road_data), len(track_data)))


if __name__ == "__main__":
    main()
