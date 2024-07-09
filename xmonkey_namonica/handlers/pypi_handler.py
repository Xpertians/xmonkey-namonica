import os
import logging
import requests
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_tar


class PypiHandler(BaseHandler):
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

    def placehldr(self):
        results = {}
        logging.info("Placeholder results...")
        results['license_files'] = {}
        results['copyrights'] = {}
        results['license'] = 'HTTP-404'
        results['url'] = self.repo_url
        self.results = results

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
        url = f"https://pypi.org/pypi/{pkg_name}/json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            license_info = data['info'].get('license')
            if not license_info:
                classifiers = data['info'].get('classifiers', [])
                for classifier in classifiers:
                    if "License ::" in classifier:
                        license_info = classifier.split(" :: ")[-1]
                        break
            if not license_info:
                license_info = 'License information not available'
            return license_info
        else:
            logging.error("Can't obtain data from Nuget Registry")
            return ''

    def construct_download_url(self):
        namespace = (
            self.purl_details['namespace'].replace('%40', '@')
            if self.purl_details['namespace']
            else self.purl_details['name']
        )
        iniName = namespace[0].lower()
        predefined_url = (
            f"https://pypi.python.org/packages/source/{iniName}/{namespace}/"
            f"{self.purl_details['name']}-"
            f"{self.purl_details['version']}.tar.gz"
        )
        package_info_url = (
            f"https://pypi.org/pypi/{self.purl_details['name']}/json"
        )
        package_info_response = requests.get(package_info_url)
        if package_info_response.status_code == 200:
            package_info = package_info_response.json()
            tar_gz_url = next(
                (url_info['url'] for url_info in package_info['urls']
                 if url_info['url'].endswith('.tar.gz')),
                None
            )
            if tar_gz_url:
                response = requests.head(tar_gz_url)
                if response.status_code == 200:
                    return tar_gz_url
        return predefined_url
