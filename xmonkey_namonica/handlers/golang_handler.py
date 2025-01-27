import os
import json
import magic
import shutil
import hashlib
import logging
import argparse
import requests
import subprocess
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
from xmonkey_lidy.matcher import LicenseMatcher
from .base_handler import BaseHandler
from urllib.parse import urlparse, parse_qs
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, check_and_extract
from ..utils import extract_zip, extract_tar, extract_bz2


class GolangHandler(BaseHandler):
    def fetch(self):
        download_url, license_txt = self.get_package_info()
        self.repo_url = download_url
        self.download_url = download_url
        if license_txt:
            lmatcher = LicenseMatcher()
            LiDy_results  = lmatcher.identify_license(
                license_txt, False, False, False
            )
            self.spdx_code = LiDy_results.get('SPDX', 'Unknown')
        else:
            self.spdx_code = ''
        with temp_directory() as temp_dir:
            self.temp_dir = temp_dir
            filename = (
                f"{self.purl_details['version']}.zip"
            )
            package_file_path = os.path.join(
                temp_dir,
                filename
            )
            rst = download_file(download_url, package_file_path)
            if rst:
                logging.info(f"Downloaded package in {self.temp_dir}")
                self.unpack()
                self.scan()
            else:
                self.placehldr()

    def get_package_info(self):
        go_proxy = "https://proxy.golang.org"
        module_path = "/".join(self.purl_details['fullparts'])
        purl_body = module_path[len("golang/"):]
        parsed_url = urlparse(purl_body)
        parts = purl_body.split("@")
        if len(parts) != 2:
            raise ValueError("Invalid PURL format. Expected '<module-path>@<version>'.")
        module_path = parts[0]
        origin_url = f"https://{module_path}"
        license_txt = ''
        if "github.com" in origin_url:
            raw_base_url = origin_url.replace("github.com", "raw.githubusercontent.com")
            branches = ["refs/heads/main", "refs/heads/master"]
            license_paths = ["LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING"]

            for branch in branches:
                for path in license_paths:
                    license_url = f"{raw_base_url}/{branch}/{path}"
                    try:
                        response = requests.get(license_url)
                        if response.status_code == 200:
                            if "Redirecting" in response.text:
                                license_txt = ''
                            else:
                                license_txt = response.text
                    except requests.exceptions.RequestException:
                        continue

        module_path = requests.utils.unquote(module_path)
        version = parts[1]
        encoded_module_path = requests.utils.quote(module_path, safe="")
        info_url = f"{go_proxy}/{encoded_module_path}/@v/{version}.info"
        try:
            response = requests.get(info_url)
            response.raise_for_status()
            package_info = response.json()
            return f"{go_proxy}/{encoded_module_path}/@v/{version}.zip", license_txt
        except requests.exceptions.RequestException as e:
            print(f"Error fetching package info: {e}")
            return None, None

    def placehldr(self):
        results = {}
        logging.info("Placeholder results...")
        results['license_files'] = {}
        results['copyrights'] = {}
        results['license'] = 'HTTP-404'
        results['url'] = self.repo_url
        self.results = results

    def unpack(self):
        if self.temp_dir:
            filename = (
                f"{self.purl_details['version']}.zip"
            )
            package_file_path = os.path.join(
                self.temp_dir,
                filename
            )
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(package_file_path)
            if 'gzip' in mimetype:
                extract_zip(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'zip' in mimetype:
                extract_zip(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'tar' in mimetype:
                extract_tar(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'bzip2' in mimetype:
                extract_bz2(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            else:
                logging.error(f"MimeType not supported {mimetype}")
                logging.error(f"Error unpacking file in {self.temp_dir}")
                exit()

    def scan(self):
        results = {}
        logging.info("Scanning package contents...")
        files = PackageManager.scan_for_files(
            self.temp_dir, ['COPYRIGHT', 'NOTICES', 'LICENSE', 'COPYING']
        )
        results['license_files'] = files
        copyhits = PackageManager.scan_for_copyright(self.temp_dir)
        results['copyrights'] = copyhits
        self.results = results
        results['license'] = self.spdx_code
        results['url'] = self.repo_url
        self.results = results

    def get_license(self):
        return self.spdx_code

    def generate_report(self):
        if not self.results['license']:
            fnd_licenses = set()
            for entry in self.results.get('license_files', []):
                if 'spdx' in entry and entry['spdx']:
                    fnd_licenses.add(str(entry['spdx']))
            if not fnd_licenses:
                fnd_licenses.add('-')
            self.results['license'] = ', '.join(fnd_licenses)
        logging.info("Generating report based on the scanned data...")
        return self.results