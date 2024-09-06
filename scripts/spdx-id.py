import os
import json
import re
import requests
from collections import Counter

SPDX_LICENSES_INDEX_URL = "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
PATTERN_FILE = 'spdx_license_patterns.json'

def download_spdx_licenses(output_file='spdx_licenses.json'):
    """ Download all SPDX licenses and store them locally in a single JSON file """
    print("Downloading SPDX license data...")
    licenses = []

    response = requests.get(SPDX_LICENSES_INDEX_URL)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the SPDX index. Status code: {response.status_code}")

    index_data = response.json()
    license_list = index_data['licenses']

    for license_info in license_list:
        license_id = license_info['licenseId']
        license_name = license_info['name']
        details_url = license_info['detailsUrl']

        license_response = requests.get(details_url)
        if license_response.status_code != 200:
            print(f"Failed to fetch license data for {license_id}. Skipping...")
            continue

        license_data = license_response.json()
        license_text = license_data.get('licenseText')

        if license_text:
            licenses.append({
                'licenseId': license_id,
                'licenseName': license_name,
                'licenseText': license_text
            })

    with open(output_file, 'w') as f:
        json.dump(licenses, f, indent=4)

    print(f"SPDX licenses downloaded and saved to {output_file}")

def load_spdx_licenses(local_file='spdx_licenses.json'):
    """ Load SPDX licenses from the local file """
    if not os.path.exists(local_file):
        raise FileNotFoundError(f"SPDX licenses file '{local_file}' not found.")
    
    with open(local_file, 'r') as f:
        return json.load(f)

def generate_license_patterns(spdx_licenses, output_file=PATTERN_FILE):
    """ Generate patterns dynamically from the SPDX license data and store them in a file """
    license_patterns = {}

    for license_data in spdx_licenses:
        license_id = license_data['licenseId']
        license_name = license_data['licenseName']
        license_text = license_data.get('licenseText')

        if not license_text:
            continue

        # Extract common phrases (like foundation names, URLs)
        foundation_names = re.findall(r'\b[A-Za-z]+\sFoundation\b', license_text, re.IGNORECASE)
        urls = re.findall(r'http[s]?://[^\s]+', license_text)

        # Ensure license name and SPDX ID are part of the pattern and deduplicate patterns
        patterns = list(set(foundation_names + urls + [license_name, license_id]))
        
        # Make all patterns case-insensitive by storing them in lowercase
        patterns = [pattern.lower() for pattern in patterns]
        
        # Ensure no pattern collisions by checking the length of the patterns
        if license_id not in license_patterns:
            license_patterns[license_id] = patterns
        else:
            # Add non-duplicate patterns to the existing license entry
            license_patterns[license_id] = list(set(license_patterns[license_id] + patterns))

    # Save the generated patterns to a JSON file
    with open(output_file, 'w') as f:
        json.dump(license_patterns, f, indent=4)

    print(f"License patterns saved to {output_file}")
    return license_patterns

def load_license_patterns(pattern_file=PATTERN_FILE):
    """ Load license patterns from the stored JSON file """
    if not os.path.exists(pattern_file):
        raise FileNotFoundError(f"Pattern file '{pattern_file}' not found.")
    
    with open(pattern_file, 'r') as f:
        return json.load(f)

def match_license_with_patterns(text, license_patterns):
    """ Match a text using license-specific patterns """
    matches = {}
    text = text.lower()  # Make the search case-insensitive
    for license_id, patterns in license_patterns.items():
        match_count = 0
        for pattern in patterns:
            if re.search(re.escape(pattern), text, re.IGNORECASE):
                match_count += 1
        if match_count > 0:
            matches[license_id] = match_count
    return matches

def match_license(text, spdx_licenses, threshold=0.5):
    """ Match a text to the closest SPDX license using Sørensen-Dice """
    preprocessed_text = preprocess(text)
    best_match = None
    highest_score = 0.0

    for license_data in spdx_licenses:
        license_id = license_data['licenseId']
        license_text = license_data.get('licenseText')

        preprocessed_license = preprocess(license_text)
        score = sorensen_dice_coefficient(preprocessed_text, preprocessed_license)

        if score > highest_score:
            highest_score = score
            best_match = license_id

    if highest_score > threshold:
        return {"SPDX": best_match, "method": "soredice_proximity_score", "score": highest_score}

    # If no match above threshold, fall back to pattern-based matching
    print("No high similarity match found. Falling back to pattern-based search.")
    license_patterns = load_license_patterns()
    matches = match_license_with_patterns(text, license_patterns)

    if matches:
        max_matches = max(matches.values())
        top_match = max(matches, key=matches.get)
        return {"SPDX": top_match, "method": "string_patterns", "score": max_matches}
    else:
        return {"SPDX": "UNKNOWN", "method": "string_patterns", "score": 0}

def preprocess(text):
    """ Preprocess the text by normalizing and tokenizing """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]+', '', text)  # Remove non-alphanumeric characters
    tokens = text.split()  # Split by whitespace
    return tokens

def sorensen_dice_coefficient(a, b):
    """ Compute Sørensen-Dice coefficient between two token sets """
    if not a or not b:
        return 0.0
    a_bigrams = Counter(zip(a, a[1:]))
    b_bigrams = Counter(zip(b, b[1:]))
    overlap = sum((a_bigrams & b_bigrams).values())
    total = sum(a_bigrams.values()) + sum(b_bigrams.values())
    return 2 * overlap / total

# If running for the first time, download the SPDX license data
if not os.path.exists('spdx_licenses.json'):
    download_spdx_licenses()

# Load the local SPDX license data
spdx_licenses = load_spdx_licenses()

# Generate and store license patterns if the pattern file does not exist
if not os.path.exists(PATTERN_FILE):
    generate_license_patterns(spdx_licenses)

# Use the NOTICE-TEST file
with open('LICENSE-EMPTY', 'r') as f:
    notice_text = f.read()

# Test matching
result = match_license(notice_text, spdx_licenses)

# Print the result as a JSON output
print(json.dumps(result, indent=4))
