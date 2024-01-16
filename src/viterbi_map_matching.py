"""
From ChatGPT.
    Sure, I can provide you with a basic example of a Python function that uses the
Viterbi algorithm to match a sequence of GPS points to a street graph.
Please note that this is a simplified example, and you may need to adapt it based
on the specific characteristics of your data and street graph representation.

Also...
In map matching, the transition probability typically represents the likelihood
of moving from one street node to another. One reasonable method to compute the
transition probability is to use the geometric or topological properties of the
street graph. Here are a few approaches you might consider...

"""

import numpy as np
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from src.config.get_config import get_database_access

global connection, cursor, max_d


def viterbi_hmm(gps_sequence, street_graph, distance_map):
    # Assuming street_graph is a dictionary where keys are street nodes and values are lists of neighboring nodes
    states = list(street_graph.keys())

    # Initialize Viterbi matrix with zeros
    viterbi_matrix = np.zeros((len(states), len(gps_sequence)))

    # Initialize back pointer matrix to store the path
    back_pointer_matrix = np.zeros((len(states), len(gps_sequence)), dtype=int)

    # Initial probabilities based on the assumption that the first GPS point is close to the
    # start node of the street graph
    viterbi_matrix[:, 0] = 1.0 / len(states)

    # Iterate through the GPS sequence
    for t in range(1, len(gps_sequence)):
        # print("-" * 40)
        for s in range(len(states)):
            # Calculate transition probabilities from the previous step to the current state
            transition_probs = [
                viterbi_matrix[prev_s, t - 1] * transition_probability(prev_s, s, states, street_graph)
                for prev_s in range(len(states))]

            # Choose the state with the maximum probability and update the Viterbi matrix and backpointer matrix
            max_prob_index = np.argmax(transition_probs)
            # print("****", max_prob_index, transition_probs[max_prob_index])
            viterbi_matrix[s, t] = (transition_probs[max_prob_index] *
                                    emission_probability(gps_sequence[t], states[s], distance_map))
            back_pointer_matrix[s, t] = max_prob_index
        # rescale current column
        scale = 1.0/np.sum(viterbi_matrix[:, t])
        for s in range(len(states)):
            viterbi_matrix[s, t] = viterbi_matrix[s, t] * scale
    # Backtrack to find the most likely path
    best_path = [np.argmax(viterbi_matrix[:, -1])]
    for t in range(len(gps_sequence) - 1, 0, -1):
        best_path.insert(0, back_pointer_matrix[best_path[0], t])

    # Map the best path to the corresponding street nodes
    matched_street_nodes = [states[i] for i in best_path]

    return matched_street_nodes


def transition_probability(prev_state, current_state, states, street_graph):
    prev_street = states[prev_state]
    current_street = states[current_state]
    adjacent_streets = street_graph[prev_street]
    if prev_street == current_street:
        return 1.0
    if current_street in adjacent_streets:
        return 1.0/(len(adjacent_streets))
    return 0.000001


def emission_probability(gps_point_id, street_id, distance_map):
    global max_d
    if street_id not in distance_map:
        # print(f"distance map - no street_id: {street_id}")
        return 0.000001
    distances = distance_map[street_id]
    if gps_point_id not in distances:
        # print(f"distance map - no point_id: {gps_point_id} for street_id: {street_id}")
        return 0.000001
    d = distances[gps_point_id]
    d_norm = d/max_d
    # print("emission_probability", gps_point_id, street_id, d, 1 - d_norm)
    return max(0, min(1, 1 - d_norm))


def get_point_ids(track_id, first_road_id):
    print(f"For track id = {track_id}")
    query = f"""
        select id, nearest_road_id from bicycle_data where track_id={track_id} order by id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    print(f"Points in track: {len(results)}")
    # trim leading points (moving away from base towards first road)
    while not results[0][1] == first_road_id:
        results.pop(0)
    return [item[0] for item in results]


def get_road_graph(track_id, first_road_id):
    global connection, cursor
    query = f"""
        select distinct on (one.osm_id, two.osm_id) 
                one.osm_id, two.osm_id, ST_Distance(one.way,two.way) as dist
        from planet_osm_line as one, planet_osm_line as two
        where one.osm_id < two.osm_id
            and one.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
            and two.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
            and not one.osm_id = two.osm_id
            and ST_Distance(one.way,two.way) = 0
        order by one.osm_id, two.osm_id;
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    # find first occurrence of first_road_id, and put element at start of list
    index = 0
    for item in results:
        id1, id2, _ = item
        if (not id1 == id2) and (id1 == first_road_id or id2 == first_road_id):
            break
        index = index + 1
    if index < len(results):
        results.insert(0, results.pop(index))
    ret = dict()
    for item in results:
        id1, id2, _ = item
        if id1 == id2:
            continue
        if id1 not in ret.keys():
            ret[id1] = []
        if id2 not in ret.keys():
            ret[id2] = []
        ret[id1].append(id2)
        ret[id2].append(id1)
    return ret


def get_road_names(track_id):
    query = f"""
        select osm_id, name from planet_osm_line, 
            (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id}) as track
        where osm_id = track.nearest_road_id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    ret = dict()
    for item in results:
        key, name = item
        if not name:
            continue
        ret[key] = name
    return ret


def build_track_point_to_road_distance_map(track_id):
    global max_d

    query = f"""
        select track.id, osm_id, ST_Distance(osm.way,ST_Transform(track.long_lat_original,3857)) as dist
        from bicycle_data as track, planet_osm_line as osm
        where track.track_id = {track_id}
            and osm.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
            and ST_Distance(osm.way,ST_Transform(track.long_lat_original,3857)) <= {max_d}
        order by track.id    
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    ret = dict()
    for item in results:
        point_key, street_key, distance = item
        # print(point_key, street_key, distance)
        if street_key not in ret:
            distance_map = dict()
            ret[street_key] = distance_map
        else:
            distance_map = ret[street_key]
        distance_map[point_key] = distance
    return ret


def print_street_graph_entry_with_names(key, road_graph, road_name):
    print(f"{road_name[key]}:: {key}")
    name_keys = list(road_name.keys())
    for other in road_graph[key]:
        if other in name_keys:
            print(f"    {road_name[other]}:: {other}")
        else:
            print(f"    <unnamed>:: {other}")


def make_connection():
    global connection, cursor
    config = get_database_access()
    connection = psycopg2.connect(**config)
    cursor = connection.cursor()


def insert_road_ids_into_db(track_id, all_ids):
    query = "insert into map_matching_roads(track_id, osm_id) values(%s,%s)"
    for osm_id in all_ids:
        cursor.execute(query, (track_id, osm_id))
    connection.commit()
    

def get_road_ids_from_db(track_id):
    query = f"select osm_id from map_matching_roads where track_id={track_id} order by id"
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return [e[0] for e in list(results)]


def compute_point_to_road_list(gps_points, matched_street_nodes, distance_map):
    ret = []
    if not len(gps_points) == len(matched_street_nodes):
        print(f"""
            Matching problem, matching street count not same as point count: 
            {len(matched_street_nodes)}, {len(gps_points)}
        """)
    else:
        for i in range(0, len(gps_points)):
            street_key = matched_street_nodes[i]
            point_key = gps_points[i]
            if point_key in distance_map[street_key]:
                distance = distance_map[street_key][point_key]
                ret.append((point_key, street_key, distance))
    return ret


def build_original_nearest_road_map(track_id):
    query = f"""
        select id, nearest_road_id, nearest_road_distance
        from bicycle_data
        where track_id={track_id}
        order by id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    ret = dict()
    for item in results:
        point_id, road_id, distance = item
        ret[point_id] = (road_id, distance)
    return ret


def insert_new_nearest_road(point_to_road_list):
    query = f"""
        INSERT INTO map_matching_results(data_id, nearest_road_id, nearest_road_distance)
        VALUES %s
        """
    execute_values(cursor, query, point_to_road_list)
    connection.commit()


def get_all_track_and_max_d():
    query = f"""
        select track_id, max_distance
        from bicycle_track
        order by track_id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return results


def clear_out_old_data():
    query = """
        TRUNCATE TABLE map_matching_roads RESTART IDENTITY
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    query = """
        TRUNCATE TABLE map_matching_results RESTART IDENTITY
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    connection.commit()


def update_results_table_with_projected_points():
    query = """
    update map_matching_results as r set long_lat_remapped = x.matched_point
    from
        (select r.id, ST_Transform(ST_ClosestPoint(line, point),4326) as matched_point
        from
            map_matching_results as r,
            (select osm_id, way as line
                from planet_osm_line) as a,
            (select id, ST_Transform(long_lat_original,3857) as point
                from bicycle_data) as b
        where
            r.data_id = b.id and r.nearest_road_id = a.osm_id)
        as x
    where x.id = r.id;
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    connection.commit()


def main():
    global connection, cursor, max_d
    make_connection()  # if successful - sets connection, cursor
    if connection:
        print("Starting...")
        clear_out_old_data()
        track_data_list = get_all_track_and_max_d()
        for item in track_data_list:
            track_id = item[0]
            max_d = item[1] * 1.3
            print(f"Processing track {track_id}, with max_d = {max_d}")
            # first_road = 8699583  # Forestdale Road
            first_road = 404611500  # Glenn Frey Dr
            # points are index into bicycle_data - first few dropped to start on first_road
            gps_points = get_point_ids(track_id, first_road)
            # road_graph keys are osm_id in planet_osm_line from nearest_road_id of selected points
            #   entry is list of 'adjacent roads'
            road_graph = get_road_graph(track_id, first_road)
            road_name = get_road_names(track_id)
            distance_map = build_track_point_to_road_distance_map(track_id)
            nearest_road_map = build_original_nearest_road_map(track_id)
            print("... got all data ...")
            matched_street_nodes = viterbi_hmm(gps_points, road_graph, distance_map)
            print("... got matching roads ...")
            probe = 0
            all_ids = []
            for road_id in matched_street_nodes:
                if road_id == probe:
                    continue
                probe = road_id
                all_ids.append(road_id)
                if road_id in road_name:
                    print(f"{road_id}::{road_name[road_id]}")
                else:
                    print(f"{road_id}::<no name>")
            print(len(all_ids))
            insert_road_ids_into_db(track_id, all_ids)
            print(len(get_road_ids_from_db(track_id)))
            point_to_road_list = compute_point_to_road_list(gps_points, matched_street_nodes, distance_map)
            print(f"Matched {len(point_to_road_list)} points")
            insert_new_nearest_road(point_to_road_list)
            print(f"Finished processing track {track_id}")
        update_results_table_with_projected_points()
        print("All road-matching points in updated to results table")
        cursor.close()
        connection.close()
        print("... done.")


if __name__ == "__main__":
    main()
