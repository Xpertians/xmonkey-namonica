import argparse
import json
import os
from .handlers.npm_handler import NpmHandler


def main():
    parser = argparse.ArgumentParser(description="Package Analyzer Tool")
    parser.add_argument("purl", type=str, help="Package URL to process")
    parser.add_argument(
        "--export", type=str,
        help="Path to export the output as a text file",
        default=None
    )
    parser.add_argument(
        "--simple", action="store_true",
        help="Print a simple list of copyrights and licenses"
    )
    args = parser.parse_args()
    if "npm" in args.purl:
        handler = NpmHandler(args.purl)
    else:
        raise ValueError("Unsupported package type")
    handler.fetch()
    result = handler.generate_report()
    license_files = [entry['content'] for entry in result['license_files']]
    licenses = list(set(license_files))
    copyhits = [entry['line'] for entry in result['copyrights']]
    copyrights = list(set(copyhits))
    if args.simple:
        print("\n".join(copyrights))
        print("\nLicense Content:\n" + "\n".join(licenses))
    else:
        print(json.dumps(result, indent=4))
    if args.export:
        with open(args.export, "w") as f:
            if args.simple:
                f.write("\n".join(copyrights))
                f.write("\nLicense Content:\n" + "\n".join(licenses))
            else:
                f.write(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
