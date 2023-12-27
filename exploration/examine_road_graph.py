import psycopg2
from psycopg2 import sql
from src.config.get_config import get_database_access

global connection, cursor


def make_name_dict(track_id):
    global connection, cursor
    query = f"""
        select distinct osm_id, name from planet_osm_line as oam, bicycle_data as bd
        where osm_id = nearest_road_id
            and track_id = {track_id}
        order by osm_id;
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return dict(results)


def make_reverse_name_dict(name_dict):
    ret = dict()
    for key in name_dict.keys():
        value = name_dict[key]
        if value in ret.keys():
            ret[value].append(key)
        else:
            ret[value] = [key]
    return ret


def get_road_graph(track_id):
    global connection, cursor
    print(f"track_id = {track_id}")
    query = f"""
        select one.osm_id, two.osm_id, ST_Distance(ST_Transform(one.way,4326),ST_Transform(two.way,4326)) as dist from
            planet_osm_line as one, planet_osm_line as two
            where one.osm_id < two.osm_id
                and one.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
                and two.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
                and not one.osm_id = two.osm_id
                and ST_Distance(ST_Transform(one.way,4326),ST_Transform(two.way,4326)) < 4
            order by one.osm_id, two.osm_id;
        """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    ret = dict()
    for item in results:
        id1, id2, _ = item
        if id1 not in ret.keys():
            ret[id1] = []
        if id not in ret.keys():
            ret[id2] = []
        ret[id1].append(id2)
        ret[id2].append(id1)
    return ret


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def main():
    global connection, cursor
    make_connection()  # if successful - sets connection, cursor
    track_id = 1
    if connection:
        name_dict = make_name_dict(track_id)
        road_id_dict = make_reverse_name_dict(name_dict)
        graph = get_road_graph(track_id)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
