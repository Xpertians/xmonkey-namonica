import requests

def fetch_gem_details(package_name, version):
    api_url = f"https://rubygems.org/api/v1/gems/{package_name}.json"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        # Extract other details
        source_code_url = data.get('source_code_uri', '')
        if source_code_url is None:
            source_code_url = ''
        homepage_url = data.get('homepage_uri', '')
        if homepage_url is None:
            homepage_url = ''
        download_url = ''
        if 'github.com' in source_code_url:
            download_url = source_code_url
        elif 'github.com' in homepage_url:
            download_url = homepage_url
        else:
            print(f"Invalid source URL: {source_code_url} {homepage_url}")
            exit()
        return download_url
    else:
        print(f"Failed to fetch data: {response.status_code}")
        exit()


# Example usage
package_name = "bsb"
package_version = "1.1.9"

github_url = fetch_gem_details(package_name, package_version)
print("GitHub URL:", github_url)
