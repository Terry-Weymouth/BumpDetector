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
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)


def git_index_limits():
    global cursor
    query_str = "select min(id), max(id) from bicycle_data where track_id=1;"
    query = sql.SQL(query_str)
    cursor.execute(query)
    results = cursor.fetchone()
    print(results)
    return results


def create_distance_list(limits):
    results = []
    for i in range(limits[0] + 1, limits[1] + 1):
        first_id = i - 1
        second_id = i
        # "ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original)
        query_str = "select ST_Distance(track1.long_lat_original,track2.long_lat_original) " \
                    + "from bicycle_data as track1, bicycle_data as track2 " \
                    + "where track1.id=%s and track2.id=%s;"
        query = sql.SQL(query_str)
        cursor.execute(query, (first_id, second_id))
        query_results = cursor.fetchone()
        d = query_results[0]
        results.append([first_id, second_id, d])
    return results


def main():
    global connection, cursor
    make_connection()
    if cursor:
        limits = git_index_limits()
        distance_list = create_distance_list(limits)
        for item in distance_list:
            if item[2] > 8.0:
                print(item)
    if cursor:
        cursor.close()
    if connection:
        connection.close()


if __name__ == "__main__":
    main()
