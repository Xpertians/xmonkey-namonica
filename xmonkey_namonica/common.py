import os
import re
import json
import magic
import pickle
import logging
from typing import List, Dict
from pkg_resources import resource_filename
from oslili import LicenseAndCopyrightIdentifier
from xmonkey_lidy.matcher import LicenseMatcher
from urllib.parse import unquote, urlparse, parse_qs
from urllib.parse import urlparse, parse_qs, unquote
from .utils import download_file, temp_directory, extract_zip, extract_tar


class PackageManager:
    @staticmethod
    def parse_purl(purl):
        logging.info(f"parse_purl {purl}")
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
        if len(path_parts) >= 3:
            result['namespace'] = unquote(path_parts[1])
        else:
            result['namespace'] = None
        name_version = name_with_version.split('@', 1)
        result['name'] = unquote(name_version[0])
        if len(name_version) > 1:
            result['version'] = name_version[1]
        else:
            result['version'] = None
        # Small ugly hack for Go
        if 'golang' in result['type']:
            if len(path_parts) == 5:
                result['name'] = path_parts[3]
                result['version'] = None
            if len(path_parts) <= 2:
                print('purl:', purl)
                raise ValueError(
                    "Invalid PURL format."
                )
        result['qualifiers'] = parse_qs(url.query)
        result['subpath'] = unquote(url.fragment) if url.fragment else None
        result['fullparts'] = path_parts
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
    def scan_for_files(
        temp_dir: str,
        patterns: List[str]
    ) -> List[Dict[str, str]]:
        lmatcher = LicenseMatcher()
        found_files = []
        for root, dirs, files in os.walk(temp_dir):
            # Exclude .git directories
            dirs[:] = [d for d in dirs if d.lower() != '.git']
            for file in files:
                if any(
                    re.search(pattern, file, re.IGNORECASE)
                    for pattern in patterns
                ):
                    file_path = os.path.join(root, file)
                    try:
                        file_text = PackageManager.read_file_content(file_path)
                        if file_text:
                            LiDy_results  = lmatcher.identify_license(
                                file_text, False, True, False
                            )
                            spdx_code = LiDy_results.get('SPDX', 'Unknown')
                            method = LiDy_results.get('method', 'Unknown')
                            score = LiDy_results.get('score', 'Unknown')
                            found_files.append({
                                "file": file_path,
                                "content": file_text,
                                "spdx": spdx_code,
                                "score": score,
                                "method": method,
                            })
                    except Exception as e:
                        logging.error(
                            f"Error processing file {file_path}: {e}"
                        )
        return found_files

    @staticmethod
    def is_readable_text_file(file_path):
        mime = magic.Magic(mime=True)
        mimetype = mime.from_file(file_path)
        if mimetype:
            if mimetype.startswith('text'):
                return True
            if mimetype == 'application/octet-stream':
                return True
        return False

    @staticmethod
    def read_file_content(file_path, encodings=['utf-8', 'iso-8859-1']):
        if PackageManager.is_readable_text_file(file_path):
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            return None
        else:
            logging.info(f"read_file_content failed {file_path}")
            return None

    @staticmethod
    def scan_for_copyright(temp_dir: str) -> List[Dict[str, str]]:
        lmatcher = LicenseMatcher()
        copyrights = []
        pattern = r"[^0-9<>,.()@a-zA-Z-\s]+"
        for root, dirs, files in os.walk(temp_dir):
            # Exclude .git directories
            dirs[:] = [d for d in dirs if d.lower() != '.git']
            for file in files:
                file_path = os.path.join(root, file)
                if PackageManager.is_readable_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                clean_line = line.strip().lower()
                                if (
                                    "copyright " in clean_line and
                                    len(clean_line) <= 50 and
                                    "yyyy" not in clean_line
                                ):
                                    clean_line = re.sub(
                                        pattern, "", clean_line
                                    )
                                    if (
                                        clean_line.startswith('copyright') or
                                        " copyright" in clean_line
                                    ):
                                        copyrs = lmatcher.extract_copyright_info(clean_line, False)
                                        if copyrs and isinstance(copyrs, list):
                                            for entry in copyrs:
                                                if isinstance(entry, dict):
                                                    year = entry.get('year', 'Unknown')
                                                    holder = entry.get('holder', 'Unknown')
                                                    copyrights.append({
                                                        "file": file_path,
                                                        "line": clean_line
                                                    })
                    except UnicodeDecodeError:
                        continue
        return copyrights

    @staticmethod
    def serialize_output(data):
        return json.dumps(data, indent=4)
