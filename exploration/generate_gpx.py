filename = "../May29_2019_BumpAndGps.txt"


def main():
    with open("output.txt", "w") as out_file:
        out_file.write("{}\n".format('<?xml version="1.0" encoding="UTF-8"?>'))
        out_file.write("{}\n".format('<gpx version="1.0">'))
        out_file.write("{}\n".format('<trk><trkseg>'))
        with open(filename, "r") as in_file:
            line = in_file.readline()
            while line:
                line = line.strip()
                parts = line.split(':',1)
                line = in_file.readline()
                entries = parts[1].split(",")
                time = entries[6]
                lat = entries[7]
                long = entries[8]
                elev = entries[9]
                if lat == 'nan' or long == 'nan' or elev == 'nan':
                    continue
                if lat == 0.0 or long == 0.0 or elev == 0.0:
                    continue
                out_file.write("<trkpt lat=\"{}\" lon=\"{}\">".format(lat,long))
                out_file.write("<ele>{}</ele>".format(elev))
                out_file.write("<time>{}</time>".format(time))
                out_file.write("</trkpt>\n")
        out_file.write("{}\n".format('</trkseg></trk>'))
        out_file.write("{}\n".format('</gpx>'))


if __name__ == "__main__":
    main()

