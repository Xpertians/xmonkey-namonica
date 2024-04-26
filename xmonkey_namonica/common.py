import os
import re
import json
from urllib.parse import unquote, urlparse, parse_qs
from urllib.parse import urlparse, parse_qs, unquote
from .utils import download_file, temp_directory, extract_zip, extract_tar


class PackageManager:
    @staticmethod
    def parse_purl(purl):
        result = {}
        url = urlparse(purl)
        if url.scheme != 'pkg':
            raise ValueError("Invalid PURL scheme")
        path_parts = url.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError(
                "Invalid PURL format. Expected at least pkg:type/name@version"
            )
        result['type'] = path_parts[0]
        name_with_version = path_parts[-1]
        if len(path_parts) == 3:
            result['namespace'] = unquote(path_parts[1])
        else:
            result['namespace'] = None
        name_version = name_with_version.split('@', 1)
        result['name'] = unquote(name_version[0])
        if len(name_version) > 1:
            result['version'] = name_version[1]
        else:
            result['version'] = None
        result['qualifiers'] = parse_qs(url.query)
        result['subpath'] = unquote(url.fragment) if url.fragment else None

        return result

    @staticmethod
    def unpack_package(file_path):
        with temp_directory() as temp_dir:
            if file_path.endswith('.zip'):
                extract_zip(file_path, temp_dir)
            elif file_path.endswith('.tar.gz') or file_path.endswith('.tar'):
                extract_tar(file_path, temp_dir)
            else:
                print(f"Unsupported file format for {file_path}")
                raise ValueError("Unsupported file format")
            print(f"Package unpacked to {temp_dir}")
            return temp_dir

    @staticmethod
    def scan_for_files(temp_dir, patterns):
        found_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if any(
                    re.match(pattern, file, re.IGNORECASE)
                    for pattern in patterns
                ):
                    file_path = os.path.join(root, file)
                    file_text = PackageManager.read_file_content(file_path)
                    found_files.append({
                        "file": file_path,
                        "content": file_text
                    })
        return found_files

    @staticmethod
    def read_file_content(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            raise

    @staticmethod
    def scan_for_copyright(temp_dir):
        copyrights = []
        pattern = "[^0-9<>,.()@a-zA-Z-\s]+"
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if ("copyright" in line.lower() and
                                    len(line) <= 50):
                                copyhit = line.strip()
                                copyhit = re.sub(pattern, "", line.strip())
                                copyrights.append({
                                    "file": file_path,
                                    "line": copyhit.strip()
                                })
                except UnicodeDecodeError:
                    continue
        return copyrights

    @staticmethod
    def serialize_output(data):
        return json.dumps(data, indent=4)
