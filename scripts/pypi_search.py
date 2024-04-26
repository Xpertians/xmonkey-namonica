import requests
from bs4 import BeautifulSoup

def search_pypi(query):
    # PyPI search URL
    url = "https://pypi.org/search/?q=" + requests.utils.quote(query)

    # Make the GET request
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch data: {response.status_code}"

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # Extract package info from the search results
    for result in soup.find_all('a', class_='package-snippet'):
        name = result.find('h3', class_='package-snippet__title').get_text(strip=True)
        version = result.find('span', class_='package-snippet__version').get_text(strip=True)
        description = result.find('p', class_='package-snippet__description').get_text(strip=True)
        results.append({'name': name, 'version': version, 'description': description})

    return results

def main():
    # Input query
    query = input("Enter keywords to search for packages: ")

    # Search for packages
    results = search_pypi(query)
    if isinstance(results, list) and results:
        for package in results:
            print(f"Package Name: {package['name']}, Version: {package['version']}")
            print(f"Description: {package['description']}\n")
    else:
        print("No results found or failed to retrieve data.")

if __name__ == "__main__":
    main()
