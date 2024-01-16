import os
import fnmatch


def get_trace_file_paths(connection, cursor, use_all=True):
    directory_path = "./data_to_use"  # Change this to the desired directory path
    pattern = "*_Cleaned.txt"
    matching_files = find_files(directory_path, pattern)
    if use_all:
        return matching_files
    else:
        return paths_not_in_database(matching_files, connection, cursor)


def find_files(directory, pattern):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            file_list.append(os.path.join(root, filename))
    return file_list


def paths_not_in_database(path_list, connection, cursor):
    query = "select file_path from bicycle_track"
    cursor.execute(query)
    results = cursor.fetchall()
    fetched_list = []
    for item in results:
        fetched_list.append((item[0]))
    print(fetched_list)
    results = []
    for candidate in path_list:
        if candidate not in fetched_list:
            results.append(candidate)
    return results
