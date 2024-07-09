import os
import magic
import logging
import requests
from .base_handler import BaseHandler
from urllib.parse import urlparse, parse_qs
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, check_and_extract
from ..utils import extract_zip, extract_tar, extract_bz2


class CondaHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        self.repo_url = download_url
        with temp_directory() as temp_dir:
            package_file_path = os.path.join(
                temp_dir,
                self.conda_pkg
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
            package_file_path = os.path.join(
                self.temp_dir,
                self.conda_pkg
            )
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(package_file_path)
            if 'gzip' in mimetype:
                extract_zip(package_file_path, self.temp_dir)
                check_and_extract(self.temp_dir, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'tar' in mimetype:
                extract_tar(package_file_path, self.temp_dir)
                check_and_extract(self.temp_dir, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'bzip2' in mimetype:
                extract_bz2(package_file_path, self.temp_dir)
                check_and_extract(self.temp_dir, self.temp_dir)
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
        channel = 'conda-forge'
        url = f"https://api.anaconda.org/package/{channel}/{pkg_name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            license_info = data.get('license', '')
            return license_info
        else:
            logging.error("Can't obtain data from Crates.IO")
            return ''

    def construct_download_url(self):
        base_url = "https://anaconda.org/conda-forge/"
        package_name = self.purl_details['name']
        version = self.purl_details['version']
        qualifiers = self.purl_details['qualifiers']
        if 'build' in qualifiers:
            build = qualifiers['build'][0]
        else:
            logging.error(f"Must provide a valid build")
            exit()
        if 'channel' in qualifiers:
            channel = qualifiers['channel'][0]
        else:
            logging.error(f"Must provide a valid channel")
            exit()
        if 'subdir' in qualifiers:
            subdir = qualifiers['subdir'][0]
        else:
            logging.error(f"Must provide a valid subdir")
            exit()
        # Form the download URL
        conda_repo = f"{base_url}{package_name}/{version}/download/{subdir}/"
        conda_pkg = f"{package_name}-{version}-{build}.tar.bz2"
        download_url = f"{conda_repo}{conda_pkg}"
        self.conda_pkg = conda_pkg
        return download_url
