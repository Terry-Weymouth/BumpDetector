import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

connection = None
cursor = None


def make_connection():
    global connection, cursor
    try:
        config = get_database_access()
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def compute_point_on_road(track_id, osm_id):
    # ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original)
    # ST_AsText(ST_ClosestPoint(track.long_lat_original,ST_Transform(osm.way,4326))) as cp
    """
    select  ST_AsText(ST_ClosestPoint(line, point)) as cp1,
        ST_AsText(ST_ClosestPoint(point, line)) as cp2,
        ST_AsText(point),
        ST_AsText(ST_ShortestLine(point, line)) as line_between1,
        ST_AsText(ST_ShortestLine(line, point)) as line_between2
    from bicycle_data as track, planet_osm_line as osm,
        LATERAL (select ST_Transform(osm.way,4326) as line from planet_osm_line where osm_id=8699583) as a,
        LATERAL (select long_lat_original as point from bicycle_data where id=27) as b
    where track.id=27 and osm.osm_id=8699583
    """
    query_str = """
    
    """
    query = sql.SQL(query_str)
    cursor.execute(query)
    query_results = cursor.fetchone()
    return query_results


def main():
    global connection, cursor
    make_connection()
    # value = compute_point_on_road(1402, 8699583)
    value_tuple = compute_point_on_road(27, 8699583)
    for i in range(0, len(value_tuple)):
        print(f"{value_tuple[i]}")
    if cursor:
        cursor.close()
    if connection:
        connection.close()


if __name__ == "__main__":
    main()
