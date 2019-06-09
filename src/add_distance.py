import argparse
import os
import math


def create_line_list(source_filepath):
    line_list = []
    with open(source_filepath) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content


def values_from_line(l):
    return l.split(",")


def line_from_values(v):
    return ",".join([str(o) for o in v])


def add_distance(line_list):
    # see, for ref, https://www.movable-type.co.uk/scripts/latlong.html
    results = []
    prev_lat = None
    prev_long = None
    for line in line_list:
        # g1, g2, g3, g4, g5, g6, time, lat, long, alt, speed
        values = values_from_line(line)
        lat = float(values[7])
        long = float(values[8])
        distance = 0.0
        if prev_lat and prev_long:
            r = 6371e3  # earth, mean radius, metres
            fe1 = math.radians(prev_lat)
            fe2 = math.radians(lat)
            del_fe = math.radians(lat - prev_lat)
            del_lambda = math.radians(long - prev_long)

            a = math.sin(del_fe / 2) * math.sin(del_fe / 2) + math.cos(fe1) * math.cos(fe2) * math.sin(del_lambda / 2) * math.sin(del_lambda / 2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = r * c  # in m
        prev_lat = lat
        prev_long = long
        values.append(distance)
        results.append(line_from_values(values))
    return results


def main():
    parser = argparse.ArgumentParser(description='Convert raw GPS/Bump data to internal; remove useless records.')
    parser.add_argument('--source', type=str, help='Require path to (raw) source data')
    parser.add_argument('--output', type=str,
                        help='Optional path to output file - default to input file path with "_cleaned" added')
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
        output = "{}_dist".format(filename)
        if file_extension:
            output = "{}{}".format(output,file_extension)
    print("Using source = " + source)
    print("  and output = " + output)
    out_list = create_line_list(source)
    print("Number of lines: {}".format(len(out_list)))
    out_list = add_distance(out_list)
    with open(output, "w") as out_file:
        for line in out_list:
            out_file.write("{}\n".format(line))


if __name__ == "__main__":
    main()
