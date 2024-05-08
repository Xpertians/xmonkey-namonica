import os
import logging
import requests
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_tar


class NpmHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        with temp_directory() as temp_dir:
            filename = (
                f"{self.purl_details['name']}-"
                f"{self.purl_details['version']}.tgz"
            )
            package_file_path = os.path.join(
                temp_dir,
                filename
            )
            download_file(download_url, package_file_path)
            logging.info(f"Downloaded package to {package_file_path}")
            self.temp_dir = temp_dir
            self.unpack()
            self.scan()

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
        pkg_name = self.purl_details['name']
        results['license'] = self.get_license(pkg_name)
        self.results = results

    def generate_report(self):
        logging.info("Generating report based on the scanned data...")
        return self.results

    def get_license(self, pkg_name):
        url = f"https://registry.npmjs.org/{pkg_name}"
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
        namespace = (
            self.purl_details['namespace'].replace('%40', '@') + '/' +
            self.purl_details['name']
            if self.purl_details['namespace']
            else self.purl_details['name']
        )
        return (
            f"https://registry.npmjs.org/"
            f"{namespace}/-/"
            f"{self.purl_details['name']}-{self.purl_details['version']}.tgz"
        )
