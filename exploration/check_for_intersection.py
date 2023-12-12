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
    query_str = "select track.id, track.nearest_road_id, osm.name " \
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
        prev_road = None
        current_road = None
        on_road = None
        seen_count = 0
        off_road = None
        for i in range(len(point_list)):
            current_road = point_list[i][1]
            if current_road == prev_road:
                seen_count += 1
            else:
                seen_count = 0
                off_road = current_road
                if not off_road == on_road:
                    print("Off Road ", point_list[i])
            if seen_count > 5 and not current_road == on_road:
                on_road = current_road
                print("On Road: ", point_list[i])
            prev_road = current_road

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    main()
