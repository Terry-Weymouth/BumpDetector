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
        geom = "ST_AsGeoJSON(long_lat_original,4326)"
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


def add_geom(out_file, geom_list):
    out_file.write("let arr = [];\n")
    for g in geom_list:
        out_file.write('arr.push(' + g[0] + ');\n')

    out_file.write("""
        const allPoints = arr.map(point => ({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: point
            }
        }));

        map.on('style.load', () => {
            map.addLayer({
                id: 'path',
                type: 'circle',
                source: {
                    type: 'geojson',
                    data: {
                        type: 'FeatureCollection',
                        features: allPoints
                    }
                }
            })
        });
    """)


def add_map_base(out_file):
    out_file.write(
        """\t\tconst map = new mapboxgl.Map({
            container: 'map',
            style: 'mapbox://styles/mapbox/streets-v12',
            center: [-83.1592,42.4939],
            zoom: 14,
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
    for point in track_geom:
        print(point)
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
const allPoints = arr.map(point => ({
    type: 'Feature',
    geometry: {
        type: 'Point',
        coordinates: point
    }
}));

map.addLayer({
    id: 'path',
    type: 'circle',
    source: {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: allPoints
        }
    }
});
"""