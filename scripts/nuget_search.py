import requests
import xml.etree.ElementTree as ET

def search_nuget_packages(query):
    # Encode the search term to ensure the URL is properly formatted
    encoded_query = requests.utils.quote(query)
    
    # NuGet API V2 endpoint for search
    url = f"https://www.nuget.org/api/v2/Search()?searchTerm='{encoded_query}'&$format=atom"

    # Make the GET request
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Failed to fetch data: {response.status_code}"

def parse_nuget_xml(xml_content):
    # Define the namespaces used in the XML document
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'd': 'http://schemas.microsoft.com/ado/2007/08/dataservices',
        'm': 'http://schemas.microsoft.com/ado/2007/08/dataservices/metadata'
    }

    # Parse the XML
    root = ET.fromstring(xml_content)
    
    # Find all entry elements in the feed
    entries = root.findall('atom:entry', ns)
    packages = []
    
    # Extract package details
    for entry in entries:
        title = entry.find('atom:title', ns).text
        # Navigate to the properties element where version information should be located
        properties = entry.find('.//m:properties', ns)
        if properties is not None:
            version_element = properties.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Version', ns)
            if version_element is not None:
                version = version_element.text
            else:
                version = "Version not found"
        else:
            version = "Properties not found"
        
        packages.append({'name': title, 'version': version})
    
    return packages


def main():
    # Input query
    query = input("Enter the package name to search: ")

    # Search for packages and get XML response
    xml_response = search_nuget_packages(query)

    # Parse XML and extract package info
    if isinstance(xml_response, str) and xml_response.startswith('<?xml'):
        packages = parse_nuget_xml(xml_response)
        for package in packages:
            print(f"Package Name: {package['name']}, Version: {package['version']}")
    else:
        print(xml_response)

if __name__ == "__main__":
    main()
