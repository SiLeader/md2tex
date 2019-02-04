import argparse
import datetime

import md
import build


def main():
    parser = argparse.ArgumentParser("md2tex", description="Markdown to TeX converter")
    parser.add_argument("--title", "-t", help="title name", default=None)
    parser.add_argument("--author", "-a", help="author", default=None)
    parser.add_argument("--date", "-d", help="date", default=None)
    parser.add_argument("--now", "-n", help="date = now", action="store_true")
    parser.add_argument("--class", "-c", help="document class (default jsarticle)", default="jsarticle")
    parser.add_argument("--output", "-o", help="output file name (default a.tex)", default="a.tex")
    parser.add_argument("--parser", "-p", choices=["markdown"], default="markdown")
    parser.add_argument("--picture-width", "--width", "-w", help="picture width (default 5cm)", default="5cm")
    parser.add_argument("input", help="input file name")

    args = parser.parse_args()

    parsers = {
        "markdown": md.MarkdownParser
    }

    parser = parsers[args.parser]()
    parts = parser.parse_file(args.input)

    date = args.date
    if args.now:
        date = datetime.datetime.now().strftime("%Y/%-m/%-d")

    build.generate(
        args.output, getattr(args, "class"), args.picture_width, parts,
        author=args.author, date=date, title=args.title)


if __name__ == '__main__':
    main()
