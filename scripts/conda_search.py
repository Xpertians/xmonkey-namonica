from urllib.parse import urlparse, parse_qs

def extract_conda_purl_details_and_download_url(purl, base_url):
    # Initial parsing of the PURL
    if not purl.startswith('pkg:conda/'):
        return "Invalid Conda PURL format"

    # Remove the 'pkg:conda/' prefix and split at the first '@' to separate the package and the version
    base_info, _, qualifiers = purl[10:].partition('?')
    package_name, _, version = base_info.partition('@')

    # Parse the qualifiers
    qualifier_dict = parse_qs(qualifiers)

    # Extracting qualifiers with default values if they do not exist
    build = qualifier_dict.get('build', [None])[0]
    channel = qualifier_dict.get('channel', [None])[0]
    subdir = qualifier_dict.get('subdir', [None])[0]

    # Form the download URL
    download_url = f"{base_url}{package_name}/{version}/download/{subdir}/{package_name}-{version}-{build}.tar.bz2"

    return {
        "package_name": package_name,
        "version": version,
        "build": build,
        "channel": channel,
        "subdir": subdir,
        "download_url": download_url
    }

# Example usage
purl = "pkg:conda/absl-py@1.3.0?build=pyhd8ed1ab_0&channel=main&subdir=noarch"
base_url = "https://anaconda.org/conda-forge/"
details = extract_conda_purl_details_and_download_url(purl, base_url)
print(details)