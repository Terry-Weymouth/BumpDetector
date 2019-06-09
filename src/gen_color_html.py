color_list = [
    (255, 0, 0),
    (229, 25, 25),
    (204, 51, 51),
    (178, 76, 76),
    (153, 102, 102),
    (127, 127, 127),
    (102, 153, 153),
    (76, 178, 178),
    (51, 204, 240),
    (25, 229, 229),
    (0, 255, 255)
]

count = 0

with open("../results/colors.html", "w") as out_file:
    out_file.write("{}\n{}\n{}\n{}\n\t{}\n\t{}\n{}\n".format(
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"UTF-8\">",
        "<title>Colors</title>",
        "</head>",
        "<body>"))
    for color in color_list:
        r,g,b = color
        out_file.write("<div style=\"background-color:rgb({},{},{})\">{}</div>".format(r,g,b,count))
        count += 1
    out_file.write("{}\n{}\n".format("</body>","</html>"))