import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

connection = None
cursor = None
max_d = 0


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def create_point_list(track_index):
    global cursor
    query_str = "select track.id, track.nearest_road_id, osm.name, speed, osm.width " \
                + "from bicycle_data as track join planet_osm_line as osm " \
                + "on (track.nearest_road_id=osm.osm_id) "\
                + "where track.track_id=%s " \
                + "order by track.id "\
                + ";"
    query = sql.SQL(query_str)
    cursor.execute(query, (track_index,))
    query_results = cursor.fetchall()
    results = []
    for r in query_results:
        results.append(list(r))
    return results


def main():
    global connection, cursor, max_d
    track_index = 1
    try:
        make_connection()
        point_list = create_point_list(track_index)
        prev_road = 0
        speed_sum = 0
        for i in range(len(point_list)):
            current_road = point_list[i][1]
            if not current_road == prev_road:
                if speed_sum < 30:
                    print("C--", point_list[i], speed_sum)
                else:
                    print(point_list[i], speed_sum)
                prev_road = current_road
                speed_sum = 0
            speed_sum += point_list[i][3]
    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
