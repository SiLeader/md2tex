import typing
import re

import parts
import parser


class MarkdownParser(parser.Parser):
    def __init__(self):
        self.__lines = []
        self.__index = 0
        self.__meta = None

    def __set_meta(self, meta):
        self.__meta = meta

    def __clear_meta(self):
        self.__meta = None

    def __get_meta(self):
        return self.__meta

    def __has_meta(self):
        return self.__get_meta() is not None

    def __meta_parser(self):
        match = re.match("<\\s*meta\\s*>\\s*(.*)\\s*<\\s*/\\s*meta\\s*>", self.current)
        if match is None:
            return None
        self.__set_meta(match.group(1))
        self.next()
        return []

    def __picture_parser(self):
        match = re.match("!\\[(\\S+)\\]\\((\\S+)\\)", self.current)
        if match is None:
            return None
        self.next()
        return [parts.Picture(match.group(2), match.group(1))]

    def __code_parser(self):
        match = re.match('```\\s*(\\S*)', self.current)
        if match is None:
            return None
        lang = match.group(1)
        self.next()
        code_block = []
        while True:
            if self.current == '```':
                break
            code_block.append(self.current)
            self.next()
        self.next()
        return [parts.CodeBlock(code_block, lang)]

    def __item_parser(self):
        match = re.match("\\s*\\+\\s*(\\S+)", self.current)
        if match is None:
            match = re.match("\\s*[0-9]+\\.\\s*(\\S+)", self.current)
            if match is None:
                return None
        self.next()
        return parts.String(match.group(1))

    def __itemize_parser(self):
        item = self.__item_parser()
        if item is None:
            return None

        res = []
        while True:
            res.append(item)
            item = self.__item_parser()
            if item is None:
                break
        return [parts.Itemize(*res)]

    def __parse_row(self) -> typing.Optional[parts.Row]:
        match = re.match("\\|\\s*(\\S+)\\s*\\|", self.current)
        if match is None:
            return None
        row = [c.strip() for c in self.current.strip(" |").split("|")]
        self.next()
        return parts.Row(*row)

    def __parse_alignment(self):
        def parse_coalignment(c: str):
            if c.startswith(":"):
                if c.endswith(":"):
                    return parts.Alignment.center
                else:
                    return parts.Alignment.left
            else:
                return parts.Alignment.right
        row = [c.strip() for c in self.current.strip(" |").split("|")]
        self.next()
        return [parse_coalignment(c) for c in row]

    def __table_parser(self):
        title_row = self.__parse_row()
        if title_row is None:
            return None
        alignments = self.__parse_alignment()

        rows = []
        while True:
            row = self.__parse_row()
            if row is None:
                break
            rows.append(row)
        caption = self.__get_meta()
        self.__clear_meta()
        return [parts.Table(title_row, alignments, *rows, caption=caption)]

    def __title_parser(self) -> typing.Optional[typing.List[parts.Part]]:
        match = re.match("(#+)\\s+(.+)", self.current)
        if match is None:
            return None

        self.next()
        return [parts.Title(len(match.group(1)), match.group(2))]

    def __parse_line(self) -> typing.List[parts.Part]:
        line = self.current
        if line == "  ":
            self.next()
            return [parts.NewLine()]
        parsers = [
            self.__title_parser,
            self.__table_parser,
            self.__itemize_parser,
            self.__picture_parser,
            self.__meta_parser,
            self.__code_parser,
        ]

        for p in parsers:
            res = p()
            if res is not None:
                return res

        self.next()
        return [parts.String(line)]

    @property
    def is_end(self) -> bool:
        return self.__index >= len(self.__lines)

    @property
    def current(self) -> str:
        return self.__lines[self.__index]

    def next(self):
        self.__index += 1

    def __parse_lines(self) -> typing.List[parts.Part]:
        res = []
        while not self.is_end:
            res.extend(self.__parse_line())
        return res

    def parse_string(self, lines: typing.List[str]):
        splitter = "#$%$#"
        new_line = splitter + "  " + splitter

        self.__lines = []
        self.__index = 0

        for line in lines:
            line = line.replace("  ", new_line)
            for l in line.split(splitter):
                self.__lines.append(l.strip())
        self.__lines.append("")
        return self.__parse_lines()

    def parse_file(self, file: str) -> typing.List[parts.Part]:
        with open(file) as fp:
            return self.parse_string(fp.readlines())
