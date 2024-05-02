import argparse
import json
import os
from .handlers.gem_handler import GemHandler
from .handlers.npm_handler import NpmHandler
from .handlers.pypi_handler import PypiHandler
from .handlers.cargo_handler import CargoHandler
from .handlers.nuget_handler import NugetHandler
from .handlers.gen_handler import GenericHandler
from .handlers.conda_handler import CondaHandler
from .handlers.github_handler import GithubHandler
from .handlers.golang_handler import GolangHandler


def main():
    parser = argparse.ArgumentParser(description="Package Analyzer Tool")
    parser.add_argument("purl", type=str, help="Package URL to process")
    parser.add_argument(
        "--export", type=str,
        help="Path to export the output as a text file",
        default=None
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Print a full list of copyrights and license files"
    )
    args = parser.parse_args()
    if "pkg:npm" in args.purl:
        handler = NpmHandler(args.purl)
    elif "pkg:cargo" in args.purl:
        handler = CargoHandler(args.purl)
    elif "pkg:pypi" in args.purl:
        handler = PypiHandler(args.purl)
    elif "pkg:nuget" in args.purl:
        handler = NugetHandler(args.purl)
    elif "pkg:golang" in args.purl:
        handler = GolangHandler(args.purl)
    elif "pkg:gem" in args.purl:
        handler = GemHandler(args.purl)
    elif "pkg:conda" in args.purl:
        handler = CondaHandler(args.purl)
    elif "pkg:generic" in args.purl:
        handler = GenericHandler(args.purl)
    elif "pkg:github" in args.purl:
        handler = GithubHandler(args.purl)
    else:
        raise ValueError("Unsupported PURL type")
    handler.fetch()
    result = handler.generate_report()
    license_files = [entry['content'] for entry in result['license_files']]
    licenses = list(set(license_files))
    copyhits = [entry['line'] for entry in result['copyrights']]
    copyrights = list(set(copyhits))
    if args.full:
        print(json.dumps(result, indent=4))
    else:
        print("\n".join(copyrights))
        if licenses:
            print("\nLicense Content:\n" + "\n".join(licenses))
    if args.export:
        with open(args.export, "w") as f:
            if args.full:
                f.write(json.dumps(result, indent=4))
            else:
                f.write("\n".join(copyrights))
                if licenses:
                    f.write("\nLicense Content:\n" + "\n".join(licenses))


if __name__ == "__main__":
    main()
