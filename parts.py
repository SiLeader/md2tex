import typing
import enum

import abc


class BuildContext:
    def __init__(self, picture_width):
        self.__picture_width = picture_width

    @property
    def picture_width(self):
        return self.__picture_width


class Alignment(enum.Enum):
    center = "c"
    left = "l"
    right = "r"


class Part(abc.ABC):
    @abc.abstractmethod
    def tex(self, context: BuildContext):
        pass


class String(Part):
    def __init__(self, string: str):
        self.__string = string

    @property
    def string(self):
        return self.__string

    def tex(self, context: BuildContext):
        return self.__string


class Title(String):
    def __init__(self, level: int, string: str):
        super(Title, self).__init__(string)
        self.__level = level - 1

    @property
    def level(self) -> int:
        return self.__level

    def tex(self, context: BuildContext):
        return "\\" + ("sub" * self.level) + "section{" + self.string + "}"


class Formula(String):
    pass


class Row(Part):
    def __init__(self, *strings: String):
        self.__strings = list(strings)

    def __getitem__(self, item: int) -> String:
        return self.__strings[item]

    def __iter__(self):
        return iter(self.__strings)

    def tex(self, context: BuildContext):
        return " & ".join(self)


class Table(Part):
    def __init__(self, title: Row, alignments: typing.List[Alignment], *lines: Row, caption=None):
        self.__title = title
        self.__lines = list(lines)
        self.__alignments = alignments
        self.__caption = caption

    @property
    def title(self):
        return self.__title

    @property
    def alignments(self) -> typing.List[Alignment]:
        return self.__alignments

    def __getitem__(self, item: int) -> Row:
        return self.__lines[item]

    def __iter__(self):
        return iter(self.__lines)

    def tex(self, context: BuildContext):
        ss = [
            "\\begin{table}[htb]",
            "\\begin{center}",
            "" if self.__caption is None else ("\\caption{" + self.__caption + "}"),
            "\\begin{tabular}{" + "{}".format("".join([a.value for a in self.alignments])) + "} \\hline"
        ]
        ss.extend([
            str(self.title.tex(context)) + " \\\\ \\hline",
            " \\\\\n".join([l.tex(context) for l in self]),
            "\\end{tabular}",
            "\\end{center}",
            "\\end{table}",
        ])
        return "\n".join(ss)


class NewLine(Part):
    def tex(self, context: BuildContext):
        return " \\\\"


class Picture(Part):
    def __init__(self, file: str, title: str):
        self.__file = file
        self.__title = title

    def tex(self, context: BuildContext):
        return "\n".join([
            "\\begin{figure}",
            "\\centering",
            "\\includegraphics[width=" + context.picture_width + "]{" + self.__file + "}",
            "\\caption{" + self.__title + "}",
            "\\end{figure}"
        ])


class Itemize(Part):
    def __init__(self, *items: String):
        self.__items = list(items)

    @property
    def items(self):
        return self.__items

    def tex(self, context: BuildContext):
        items = [
            "\\begin{itemize}"
        ]
        items.extend(["\\item {}".format(i.tex(context)) for i in self.items])
        items.append("\\end{itemize}")
        return "\n".join(items)


class Enumerate(Itemize):
    def tex(self, context: BuildContext):
        items = [
            "\\begin{enumerate}"
        ]
        items.extend(["\\item {}".format(i) for i in self.items])
        items.append("\\end{enumerate}")
        return "\n".join(items)
