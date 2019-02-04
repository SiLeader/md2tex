import parts
import typing


def generate(file: str, doc_class: str, picture_width, ps: typing.List[parts.Part], author=None, date=None, title=None):
    context = parts.BuildContext(picture_width)
    with open(file, "w") as fp:
        fp.write("\n".join([
            "\\documentclass{" + doc_class + "}",
            "\\usepackage[dvipdfmx]{graphicx}",
            ""
        ]))
        maketitle = False
        if author is not None:
            fp.write("\\author{" + "{}".format(author) + "}\n")
            maketitle = True
        if date is not None:
            fp.write("\\date{" + "{}".format(date) + "}\n")
            maketitle = True
        if title is not None:
            fp.write("\\title{" + "{}".format(title) + "}\n")
            maketitle = True

        fp.write("\n".join([
            "\\begin{document}",
            ""
        ]))
        if maketitle:
            fp.write("\\maketitle\n")
        fp.write("\n".join([p.tex(context) for p in ps]))
        fp.write("\n".join([
            "",
            "\\end{document}",
            ""
        ]))
