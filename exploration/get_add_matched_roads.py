import psycopg2
from src.config.get_config import get_database_access

global connection, cursor


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def get_road_ids_from_db(track_id):
    query = f"select osm_id from map_matching_roads where track_id={track_id} order by id"
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return [e[0] for e in list(results)]


def main():
    global connection, cursor
    make_connection()  # if successful - sets connection, cursor
    track_id = 2
    should_be = [8699583, 8688834, 992526123, 107384593, 404611500, 1070134475, 8688836, 8670713, 1134277550, 992521504, 955158555, 8706804, 8693004, 460783874, 8681747, 725387069, 39369060, 8696480, 8708560, 8705205, 8695203, 8684101, 853584290, 8696078, 8696480, 39369060, 725387069, 971947462, 107384581, 107384569, 107384675, 8688343, 8700755, 1134261479, 8716806, 107384610, 8713029, 8715654, 8690303, 8701122, 8694873, 8693007, 8687772, 8718293, 418972731, 418973276, 8670713, 8688836, 1070134475, 107384604, 107384593, 992526123, 8688834, 8699583]
    check = get_road_ids_from_db(track_id)
    print(should_be)
    print(check)
    diffs = []
    if len(check) == len(should_be):
        for i in range(len(should_be)):
            if check[i] == should_be[i]:
                continue
            diffs.append((check[i], should_be[i]))
    else:
        print("different lengths")
        exit(-1)
    if not diffs:
        print("no diffs")
        exit(0)
    for item in diffs:
        print(f"check {item[0]} should be {item[1]}")


if __name__ == "__main__":
    main()
