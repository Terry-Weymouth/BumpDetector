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
    if current_state in adjacent_streets:
        return 1.0/(len(adjacent_streets))
    return 0.000001


def emission_probability(gps_point_id, street_id, distance_map):
    global max_d
    # print(gps_point_id, street_id)
    if street_id not in distance_map:
        # print(f"no street_id: {street_id}")
        return 0.000001
    distances = distance_map[street_id]
    if gps_point_id not in distances:
        # print(f"no point_id: {gps_point_id}")
        return 0.000001
    d = distances[gps_point_id]
    d_norm = d/max_d
    # print("emission_probability", gps_point_id, street_id, d, 1 - d_norm)
    return max(0, min(1, 1 - d_norm))


def get_point_ids(track_id, first_road_id):
    query = f"""
        select id, nearest_road_id from bicycle_data where track_id={track_id} order by id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    # trim leading points (moving away from base towards first road)
    while not results[0][1] == first_road_id:
        results.pop(0)
    return [item[0] for item in results]


def get_road_graph(track_id, first_road_id):
    global connection, cursor
    query = f"""
        select distinct on (one.osm_id, two.osm_id) 
                one.osm_id, two.osm_id, ST_Distance(ST_Transform(one.way,4326),ST_Transform(two.way,4326)) as dist
        from planet_osm_line as one, planet_osm_line as two
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
        select track.id, osm_id, ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) as dist
        from bicycle_data as track, planet_osm_line as osm
        where track.track_id = {track_id}
            and osm.osm_id in (select distinct nearest_road_id from bicycle_data bd where bd.track_id={track_id})
            and ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original) < {max_d};    
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    ret = dict()
    for item in results:
        point_key, street_key, distance = item
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


def main():
    global connection, cursor, max_d
    make_connection()  # if successful - sets connection, cursor
    track_id = 2
    max_d = 20
    if connection:
        first_road = 8699583

        # points are index into bicycle_data
        gps_points = get_point_ids(track_id, first_road)
        # road_graph keys are osm_id in planet_osm_line from nearest_road_id of selected points
        #   entry is list of 'adjacent roads'
        road_graph = get_road_graph(track_id, first_road)
        road_name = get_road_names(track_id)
        distance_map = build_track_point_to_road_distance_map(track_id)
        matched_street_nodes = viterbi_hmm(gps_points, road_graph, distance_map)
        probe = 0
        all_ids = []
        for id in matched_street_nodes:
            if id == probe:
                continue
            probe = id
            all_ids.append(id)
            if id in road_name:
                print(f"{id}::{road_name[id]}")
            else:
                print(f"{id}::<no name>")
        print(all_ids)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
