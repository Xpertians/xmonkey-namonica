import argparse
from .handlers.npm_handler import NpmHandler


def main():
    parser = argparse.ArgumentParser(description="Package Analyzer Tool")
    parser.add_argument("purl", type=str, help="Package URL to process")
    args = parser.parse_args()
    if "npm" in args.purl:
        handler = NpmHandler(args.purl)
    else:
        raise ValueError("Unsupported package type")
    handler.fetch()


if __name__ == "__main__":
    main()
