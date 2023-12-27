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
max_d = 10


def viterbi_hmm(gps_sequence, street_graph):
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
        for s in range(len(states)):
            # Calculate transition probabilities from the previous step to the current state
            transition_probs = [viterbi_matrix[prev_s, t - 1] * transition_probability(prev_s, s) for prev_s in
                                range(len(states))]

            # Choose the state with the maximum probability and update the Viterbi matrix and backpointer matrix
            max_prob_index = np.argmax(transition_probs)
            viterbi_matrix[s, t] = transition_probs[max_prob_index] * emission_probability(gps_sequence[t], states[s])
            back_pointer_matrix[s, t] = max_prob_index

    # Backtrack to find the most likely path
    best_path = [np.argmax(viterbi_matrix[:, -1])]
    for t in range(len(gps_sequence) - 1, 0, -1):
        best_path.insert(0, back_pointer_matrix[best_path[0], t])

    # Map the best path to the corresponding street nodes
    matched_street_nodes = [states[i] for i in best_path]

    return matched_street_nodes


def transition_probability(prev_state, current_state):
    print(prev_state, current_state)
    # Placeholder function for transition probability, you should replace it with your own logic
    return 0.5


def emission_probability(gps_point, street_node):
    global max_d
    d = distance_to_road(gps_point, street_node)
    if d > max_d:
        return 0
    d_norm = (d/max_d)**2
    return max(0, min(1, 1 - d_norm))


def distance_to_road(gps_point, street_node):
    global cursor
    query = f"""
        select osm.osm_id, ST_Distance(ST_Transform(osm.way,4326),track.long_lat_original)
        from bicycle_data as track, planet_osm_line as osm where track.id={gps_point}
        and osm.osm_id={street_node};
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchone()
    return results[0]


def get_road_ids(track_id):
    global cursor
    query = f"""
        select distinct nearest_road_id as id from bicycle_data where track_id={track_id} order by id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return [item[0] for item in results]


def get_point_ids(track_id):
    query = f"""
        select id from bicycle_data where track_id={track_id} order by id
    """
    query = sql.SQL(query)
    # noinspection PyUnresolvedReferences
    cursor.execute(query)
    # noinspection PyUnresolvedReferences
    results = cursor.fetchall()
    return [item[0] for item in results]


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
        points = get_point_ids(track_id)
        roads = get_road_ids(track_id)
        road_graph = get_road_graph(track_id)
        viterbi_hmm(points, road_graph)
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
