import os
import logging
import requests
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_zip


class NugetHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        self.repo_url = download_url
        with temp_directory() as temp_dir:
            filename = (
                f"{self.purl_details['name']}-"
                f"{self.purl_details['version']}.zip"
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
                f"{self.purl_details['version']}.zip"
            )
            package_file_path = os.path.join(
                self.temp_dir,
                filename
            )
            extract_zip(package_file_path, self.temp_dir)
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

    def get_license(self, pkg_name):
        pkg_name = pkg_name.lower()
        url = (
            "https://api.nuget.org/v3/registration5-semver1/"
            f"{pkg_name}/index.json"
        )
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            reg_page_data = data['items'][-1]
            reg_data = None
            if 'items' in reg_page_data:
                reg_data = reg_page_data
            else:
                reg_leaf_url = reg_page_data['@id']
                response = requests.get(reg_leaf_url)
                if response.status_code == 200:
                    reg_data = response.json()
                else:
                    logging.error("Can't obtain data from Nuget Registry")
                    return ''
            l_vdata = reg_data['items'][-1]['catalogEntry']
            license_expression = l_vdata.get('licenseExpression', '')
            license_url = l_vdata.get('licenseUrl', '')
            if not license_expression:
                license_expression = license_url
            return license_expression
        else:
            logging.error("Can't obtain data from Nuget Registry")
            return ''

    def construct_download_url(self):
        namespace = (
            self.purl_details['namespace'].replace('%40', '@')
            if self.purl_details['namespace']
            else self.purl_details['name']
        )
        return (
            f"https://www.nuget.org/api/v2/package/"
            f"{self.purl_details['name']}/"
            f"{self.purl_details['version']}"
        )
