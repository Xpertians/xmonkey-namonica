import os
import logging
import requests
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_tar


class NpmHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        self.repo_url = download_url
        with temp_directory() as temp_dir:
            filename = (
                f"{self.purl_details['name']}-"
                f"{self.purl_details['version']}.tgz"
            )
            package_file_path = os.path.join(
                temp_dir,
                filename
            )
            rst = download_file(download_url, package_file_path)
            if rst:
                logging.info(f"Downloaded package to {package_file_path}")
                self.temp_dir = temp_dir
                self.unpack()
                self.scan()
            else:
                self.placehldr()

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
                f"{self.purl_details['name']}-"
                f"{self.purl_details['version']}.tgz"
            )
            package_file_path = os.path.join(
                self.temp_dir,
                filename
            )
            extract_tar(package_file_path, self.temp_dir)
            logging.info(f"Unpacked package in {self.temp_dir}")

    def scan(self):
        results = {}
        logging.info("Scanning package contents...")
        files = PackageManager.scan_for_files(
            self.temp_dir, ['COPYRIGHT', 'NOTICES', 'LICENSE', 'COPYING']
        )
        results['license_files'] = files
        copyhits = PackageManager.scan_for_copyright(self.temp_dir)
        results['copyrights'] = copyhits
        results['license'] = self.get_license()
        results['url'] = self.repo_url
        self.results = results

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

    def get_license(self):
        url = f"https://registry.npmjs.org/{self.get_pkg_name()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['dist-tags']['latest']
            license_info = data['versions'][latest_version].get('license', '')
            return license_info
        else:
            logging.error("Can't obtain data from NPM")
            return ''

    def construct_download_url(self):
        return (
            f"https://registry.npmjs.org/"
            f"{self.get_pkg_name()}/-/"
            f"{self.purl_details['name']}-{self.purl_details['version']}.tgz"
        )

    def get_pkg_name(self):
        return (
            self.purl_details['namespace'].replace('%40', '@') + '/' +
            self.purl_details['name']
            if self.purl_details['namespace']
            else self.purl_details['name']
        )
