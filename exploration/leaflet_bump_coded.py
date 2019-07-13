import argparse
import os
import numpy as np

header_filepath = "../leaflet/leaflet_header.txt"
footer_filepath = "../leaflet/leaflet_footer.txt"

max_coded_value = 0.0
color_list = [
    (0, 255, 255),
    (25, 229, 229),
    (51, 204, 240),
    (76, 178, 178),
    (102, 153, 153),
    (127, 127, 127),
    (153, 102, 102),
    (178, 76, 76),
    (204, 51, 51),
    (229, 25, 25),
    (255, 0, 0)
]


def print_bounding_box(out_file):
    bound_upper = 42.494433
    bound_lower = 42.493725
    bound_left = -83.159279
    bound_right = -83.158586

    out_file.write("\t{}\n".format("var polygon = L.polygon(["))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_left))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_right))
    out_file.write("\t\t[{}, {}], ".format(bound_lower, bound_right))
    out_file.write("\t\t[{}, {}] ".format(bound_lower, bound_left))
    out_file.write("\t{}\n".format("]).addTo(mymap);"))


def create_point_list(file_path):
    global max_coded_value
    with open(file_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    table = np.array([x.split(",") for x in content])
    g1 = table[:, 0].astype(np.float)
    g2 = table[:, 1].astype(np.float)
    g3 = table[:, 2].astype(np.float)
    g4 = table[:, 3].astype(np.float)
    g5 = table[:, 4].astype(np.float)
    g6 = table[:, 5].astype(np.float)

    # time = table[:, 6].astype(np.datetime64)

    lat = table[:, 7].astype(np.float)
    long = table[:, 8].astype(np.float)
    # alt = table[:, 9].astype(np.float)
    # speed = table[:, 10].astype(np.float)

    max_g = np.maximum(g1, g2)
    max_g = np.maximum(max_g, g3)
    max_g = np.maximum(max_g, g4)
    max_g = np.maximum(max_g, g5)
    max_g = np.maximum(max_g, g6)

    # base_time = time[0]
    # delta_time = [(probe - base_time).item().total_seconds() for probe in time]

    max_coded_value = np.amax(max_g)

    point_list = []
    for i in range(len(max_g)):
        point_list.append([lat[i], long[i], max_g[i]])
    return point_list


def annotate_point_list(point_list):
    global max_coded_value
    global color_list
    index_limit = len(color_list)
    results = []
    for record in point_list:
        value = record[2]  # max_g
        index = int((value/max_coded_value) * float(index_limit))
        if index >= index_limit:
            index = index_limit - 1
        record.append(index)
        results.append(record)
    return results


def segment_point_list(annotated_point_list):
    segment_index = annotated_point_list[0][3]
    cache = []
    results = []
    for record in annotated_point_list:
        color_index = record[3]
        if not color_index == segment_index:
            cache.append(record)
            results.append([segment_index, cache])
            segment_index = color_index
            cache = []
        cache.append(record)
    if len(cache) == 1:
        cache.append(cache[0])
    results.append([segment_index, cache])
    return results


def print_trace_data(out_file, segmented_point_list):
    global color_list
    count = 0
    for segment in segmented_point_list:
        color = color_list[segment[0]]
        r, g, b = color
        var_name = "latLongs{}".format(count)
        res_name = "ployline{}".format(count)
        count += 1
        out_file.write("\tvar {} = [\n".format(var_name))
        for record in segment[1]:
            lat = record[0]
            long = record[1]
            out_file.write("\t\t[{}, {}],\n".format(lat, long))
        out_file.write("\t];\n")
        out_file.write("\t{} = L.polyline({}, {}color: 'rgb({},{},{})'{} ).addTo(mymap);\n".format(
            res_name, var_name, "{", r, g, b, "}"))


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def main():
    parser = argparse.ArgumentParser(description='Generate leaflet map of bump data')
    parser.add_argument('--source', type=str, help='Require path to (raw) source data')
    parser.add_argument(
        '--output', type=str,
        help='Optional path to output html file - default to input file path with "_bump_map" added and extension ".html"')
    args = parser.parse_args()
    source = args.source
    if not source:
        print("**********************************")
        print("The --source argument is required.")
        print("**********************************")
        parser.print_help()
        exit(-1)
    output = args.output
    if not output:
        filename, file_extension = os.path.splitext(source)
        output = "{}_bump_map.html".format(filename)
    filename, file_extension = os.path.splitext(output)
    if not file_extension == ".html":
        print("********************************************")
        print("The --output file extension must be '.html'.")
        print("********************************************")
        parser.print_help()
        exit(-1)
    print("Using source = " + source)
    print("  and output = " + output)

    point_list = create_point_list(source)
    annotated_point_list = annotate_point_list(point_list)
    segmented_point_list = segment_point_list(annotated_point_list)
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        print_bounding_box(out_file)
        print_trace_data(out_file, segmented_point_list)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
