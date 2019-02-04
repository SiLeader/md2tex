import typing
import abc

import parts


class Parser(abc.ABC):
    @abc.abstractmethod
    def parse_string(self, lines: typing.List[str]):
        pass

    @abc.abstractmethod
    def parse_file(self, file: str) -> typing.List[parts.Part]:
        pass
