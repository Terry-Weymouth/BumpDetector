import argparse
import os

header_filepath = "../leaflet/leaflet_header.txt"
footer_filepath = "../leaflet/leaflet_footer.txt"


def print_bounding_box(out_file):
    bound_upper = 42.494433
    bound_lower = 42.493725
    bound_left = -83.159279
    bound_right = -83.158586

    out_file.write("\t{}\n".format("var polygon = L.polygon(["))
    out_file.write("\t\t[{}, {}], ".format(bound_upper,bound_left))
    out_file.write("\t\t[{}, {}], ".format(bound_upper, bound_right))
    out_file.write("\t\t[{}, {}], ".format(bound_lower,bound_right))
    out_file.write("\t\t[{}, {}] ".format(bound_lower, bound_left))
    out_file.write("\t{}\n".format("]).addTo(mymap);"))


def close_enough(a, b):
    epsilon = 0.00000001
    return abs(a - b) < epsilon


def create_point_list(source_filepath):
    point_list = []
    with open(source_filepath, "r") as in_file:
        line = in_file.readline()
        while line:
            line = line.strip()
            entries = line.split(",")
            line = in_file.readline()
            lat = entries[7]
            long = entries[8]
            point_list.append([lat, long])
    return point_list


def print_trace_data(out_file, point_list):
    out_file.write("\t{}\n".format("var latlngs1 = ["))
    for index in range(0, len(point_list)):
        lat = point_list[index][0]
        long = point_list[index][1]
        out_file.write("\t\t[{}, {}],\n".format(lat, long))
    out_file.write("\t{}\n".format("];"))
    out_file.write("\t{}\n".format("var polyline1 = L.polyline(latlngs1, {color: 'red'}).addTo(mymap);"))


def copy_path_content(in_path, out_file):
    with open(in_path, "r") as in_file:
        out_file.write(in_file.read())


def main():
    parser = argparse.ArgumentParser(description='Convert raw GPS/Bump data to internal; remove useless records.')
    parser.add_argument('--source', type=str, help='Require path to (raw) source data')
    parser.add_argument(
        '--output', type=str,
        help='Optional path to output html file - default to input file path with "_map" added and extension ".html"')
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
        output = "{}_map.html".format(filename)
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
    with open(output, "w") as out_file:
        copy_path_content(header_filepath, out_file)
        print_bounding_box(out_file)
        print_trace_data(out_file, point_list)
        copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
