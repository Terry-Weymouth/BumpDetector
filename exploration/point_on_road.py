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
    # "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original)
    query_str = f"""
        select track.id, osm_id, 
            ST_AsText(ST_ClosestPoint(track.long_lat_original,ST_Transform(osm.way,4326))) as cp,
            ST_AsText(track.long_lat_original)
        from bicycle_data as track, planet_osm_line as osm
        where track.id = {track_id} and osm.osm_id = {osm_id}
    """
    query = sql.SQL(query_str)
    cursor.execute(query)
    query_results = cursor.fetchone()
    return query_results


def main():
    global connection, cursor
    make_connection()
    value = compute_point_on_road(1402, 8699583)
    print(f"{value}")
    if cursor:
        cursor.close()
    if connection:
        connection.close()


if __name__ == "__main__":
    main()
