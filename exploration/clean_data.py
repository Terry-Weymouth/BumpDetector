import argparse
import os

# home base, ignore any data inside this lat-long box
bound_upper = 42.494433
bound_lower = 42.493725
bound_left = -83.159279
bound_right = -83.158586


def close_enough(a, b):
    epsilon = 0.00000001
    return abs(a - b) < epsilon


def create_line_list(source_filepath):
    line_list = []
    with open(source_filepath, "r") as in_file:
        line = in_file.readline()
        last_lat = 0.0
        last_long = 0.0
        while line:
            line = line.strip()
            parts = line.split(':', 1)
            line = in_file.readline()
            entries = parts[1].split(",")
            lat = entries[7]
            long = entries[8]
            if lat == 'nan' or long == 'nan':
                continue
            lat = float(lat)
            long = float(long)
            if close_enough(lat, 0.0) or close_enough(long, 0.0):
                continue
            if close_enough(last_lat, lat) and close_enough(last_long, long):
                continue
            if lat < bound_upper and lat > bound_lower and long > bound_left and long < bound_right:
                continue
            last_lat = lat
            last_long = long
            line_list.append(parts[1])
    return line_list


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
        output = "{}_cleaned".format(filename)
        if file_extension:
            output = "{}{}".format(output,file_extension)
    print("Using source = " + source)
    print("  and output = " + output)
    out_list = create_line_list(source)
    print("Number of lines: {}".format(len(out_list)))
    with open(output, "w") as out_file:
        for line in out_list:
            out_file.write("{}\n".format(line))


if __name__ == "__main__":
    main()
