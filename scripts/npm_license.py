import requests

def get_license_from_npm(package_name, version=None):
    """
    Fetch license information for a given NPM package and version.
    If no version is specified, it will fetch the latest available version.
    """
    if version:
        # If a specific version is given, construct the URL for that version
        url = f"https://registry.npmjs.org/{package_name}/{version}"
    else:
        # If no version is given, fetch the latest version
        url = f"https://registry.npmjs.org/{package_name}"
    
    # Send a GET request to the NPM registry API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Load the JSON data from the response
        data = response.json()
        
        # Get the license from the package info
        license_info = data.get('license') or data.get('info', {}).get('license')
        
        # Return the license, or a message if not available
        return license_info if license_info else "License information not available"
    else:
        # Handle cases where the request failed
        return "Failed to fetch package information"

# Example usage
package_name = "react"  # Replace with your desired package name
version = "16.13.1"     # Replace with your desired version or use None for the latest
license_info = get_license_from_npm(package_name, version)
print(f"The license for {package_name} version {version} is: {license_info}")
