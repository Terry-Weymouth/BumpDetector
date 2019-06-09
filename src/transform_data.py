filename = "../May19_2019_Bump.txt"


def main():
    with open("output.txt", "w") as out_file:
        with open(filename, "r") as in_file:
            contents = in_file.read()
        n = 0
        end = -1
        l_end = len(contents)
        while end < l_end:
            n += 1
            start, end = line_bounds(contents, end + 1, n)
            out_file.write(contents[start: end])
            out_file.write("\n")


def line_bounds(contents, probe, n):
    pos = contents.find(":", probe)
    back = back_for_n(n)
    start = pos - back
    end = contents.find(":", pos + 1)
    if end < 0:
        end = len(contents)
    else:
        end = end - back_for_n(n - 1)
    return start, end


def back_for_n(n):
    back = 1
    if n > 9:
        back = 2
    if n > 99:
        back = 3
    if n > 999:
        back = 4
    if n > 9999:
        back = 5
    return back


if __name__ == "__main__":
    main()
