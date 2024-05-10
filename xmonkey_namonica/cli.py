import argparse
import json
from .handlers.gem_handler import GemHandler
from .handlers.npm_handler import NpmHandler
from .handlers.pypi_handler import PypiHandler
from .handlers.cargo_handler import CargoHandler
from .handlers.nuget_handler import NugetHandler
from .handlers.gen_handler import GenericHandler
from .handlers.conda_handler import CondaHandler
from .handlers.github_handler import GithubHandler
from .handlers.golang_handler import GolangHandler


def process_purl(purl):
    if "pkg:npm" in purl:
        handler = NpmHandler(purl)
    elif "pkg:cargo" in purl:
        handler = CargoHandler(purl)
    elif "pkg:pypi" in purl:
        handler = PypiHandler(purl)
    elif "pkg:nuget" in purl:
        handler = NugetHandler(purl)
    elif "pkg:golang" in purl:
        handler = GolangHandler(purl)
    elif "pkg:gem" in purl:
        handler = GemHandler(purl)
    elif "pkg:conda" in purl:
        handler = CondaHandler(purl)
    elif "pkg:generic" in purl:
        handler = GenericHandler(purl)
    elif "pkg:github" in purl:
        handler = GithubHandler(purl)
    else:
        raise ValueError("Unsupported PURL type")
    handler.fetch()
    return handler.generate_report()


def main():
    parser = argparse.ArgumentParser(description="Package Analyzer Tool")
    parser.add_argument(
        "input",
        type=str,
        help="Package URL or path to OSPI file with PURLs"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Path to export the output as a text file",
        default=None
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print a full list of copyrights and license files"
    )
    args = parser.parse_args()

    try:
        # Check if input is a file
        if args.input.endswith(".txt"):
            with open(args.input, 'r') as file:
                purls = file.readlines()
        else:
            purls = [args.input]

        results = []
        for purl in purls:
            purl = purl.strip()
            if purl:
                result = process_purl(purl)
                results.append(result)
                if args.full:
                    print(json.dumps(result, indent=4))
                else:
                    copyrights = list(
                        set([entry['line'] for entry in result['copyrights']])
                    )
                    print("\n".join(copyrights))
                    licenses = list(
                        set(
                            entry['content']
                            for entry in result['license_files']
                        )
                    )
                    if licenses:
                        print("\nLicense Content:\n" + "\n".join(licenses))

        if args.export:
            with open(args.export, "w") as f:
                if args.full:
                    f.write(json.dumps(results, indent=4))
                else:
                    for result in results:
                        copyrights = list(
                            set(
                                entry['line']
                                for entry in result['copyrights']
                            )
                        )
                        f.write("\n".join(copyrights))
                        licenses = list(
                            set(
                                entry['content']
                                for entry in result['license_files']
                            )
                        )
                        if licenses:
                            f.write(
                                "\nLicense Content:\n" + "\n".join(licenses)
                            )

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
