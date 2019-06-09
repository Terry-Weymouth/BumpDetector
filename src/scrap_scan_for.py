filename = "../May29_2019_BumpAndGps.txt"


def main():
    minLat = 42.494119333
    maxLat = minLat
    minLong = -83.158974667
    maxLong = minLong
    with open(filename, "r") as in_file:
        line = in_file.readline()
        while line:
            line = line.strip()
            parts = line.split(':',1)
            line = in_file.readline()
            entries = parts[1].split(",")
            if entries[7] == "nan":
                continue
            if entries[8] == "nan":
                continue
            lat = float(entries[7])
            long = float(entries[8])
            if not lat == 0:
                minLat = min(minLat, lat)
                maxLat = max(maxLat, lat)
            if not long == 0:
                minLong = min(minLong, long)
                maxLong = max(maxLong, long)
    print(minLat, maxLat, minLong, maxLong)

if __name__ == "__main__":
    main()

