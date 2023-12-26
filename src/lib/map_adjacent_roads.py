import psycopg2
from src.config.get_config import get_database_access


def connect_and_query():
    connection = None
    cursor = None
    record = None
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        query = """
            select ST_AsGeoJSON(ST_Transform(way,4326))
                from (select distinct nearest_road_id as id from bicycle_data) as roads
                join planet_osm_line as osm
                    on (roads.id=osm.osm_id)
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
