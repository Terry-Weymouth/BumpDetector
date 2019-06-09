import argparse
import os


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

    # point_list = create_point_list(source)
    # annotated_point_list = annotate_point_list(point_list)
    # segmented_point_list = segment_point_list(annotated_point_list)
    # with open(output, "w") as out_file:
    #     copy_path_content(header_filepath, out_file)
    #     print_bounding_box(out_file)
    #     print_trace_data(out_file, segmented_point_list)
    #     copy_path_content(footer_filepath, out_file)


if __name__ == "__main__":
    main()
