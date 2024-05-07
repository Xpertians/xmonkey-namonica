import requests

def get_license_from_pypi(package_name):
    """Fetch license information for a given PyPI package."""
    # Construct the URL for the PyPI JSON API
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    # Send a GET request to the PyPI API
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Load the JSON data from the response
        data = response.json()
        
        # Get the license from the package info
        license = data.get('info', {}).get('license')
        
        # Return the license, or a message if not available
        return license if license else "License information not available"
    else:
        # Handle cases where the request failed
        return "Failed to fetch package information"

# Example usage
package_name = "numpy"
package_name = "xmonkey-curator"
package_name = "scancode-toolkit"
license_info = get_license_from_pypi(package_name)
print(f"The license for {package_name} is: {license_info}")
