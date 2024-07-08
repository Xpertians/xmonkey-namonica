import os
import magic
import shutil
import hashlib
import logging
import requests
import subprocess
from bs4 import BeautifulSoup
from .base_handler import BaseHandler
from urllib.parse import urlparse, parse_qs
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory
from ..utils import extract_tar, extract_zip


class GemHandler(BaseHandler):
    def fetch(self):
        repo_url = self.construct_repo_url()
        self.repo_url = repo_url
        with temp_directory() as temp_dir:
            self.temp_dir = temp_dir
            if 'rubygem' in repo_url:
                self.fetch_file(repo_url)
                logging.info(f"File downloaded in {self.temp_dir}")
                self.unpack()
            else:
                self.clone_repo(repo_url)
                logging.info(f"Repo cloned to {self.temp_dir}")
            self.scan()

    def construct_repo_url(self):
        pkg_name = self.purl_details['name']
        pkg_version = self.purl_details['version']
        download_url = (
            f"https://rubygems.org/downloads/{pkg_name}-{pkg_version}.gem"
        )
        response = requests.get(download_url)
        if response.status_code == 200:
            return download_url
        else:
            api_url = f"https://rubygems.org/api/v1/gems/{pkg_name}.json"
            logging.info(f"api_url: {api_url}")
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                gem_url = data.get('gem_uri', '')
                if gem_url is None:
                    gem_url = ''
                source_code_url = data.get('source_code_uri', '')
                if source_code_url is None:
                    source_code_url = ''
                homepage_url = data.get('homepage_uri', '')
                if homepage_url is None:
                    homepage_url = ''
                repo_url = ''
                if 'rubygems.org' in gem_url:
                    return gem_url
                elif 'github.com' in source_code_url:
                    repo_url = source_code_url
                elif 'github.com' in homepage_url:
                    repo_url = homepage_url
                else:
                    logging.error(
                        f"Invalid source URL: {source_code_url} {homepage_url}"
                    )
                    exit()
            else:
                logging.error(f"Failed to fetch data: {response.status_code}")
                exit()
            return f"{repo_url}.git"

    def unpack(self):
        if self.temp_dir:
            package_file_path = os.path.join(
                self.temp_dir,
                "downloaded_file"
            )
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(package_file_path)
            if 'gzip' in mimetype:
                extract_zip(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'tar' in mimetype:
                extract_tar(package_file_path, self.temp_dir)
                extract_tar(self.temp_dir+'/data.tar.gz', self.temp_dir)
                # extract_tar(self.temp_dir+'/metadata.gz', self.temp_dir)
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
        url = f"https://rubygems.org/api/v1/gems/{pkg_name}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            license_info = data.get('licenses') or data.get('license')
            if license_info:
                if isinstance(license_info, list):
                    return ', '.join(license_info)
                return license_info
            else:
                return ''
        else:
            logging.error("Can't obtain data from Crates.IO")
            return ''

    def fetch_file(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            file_data = response.content
            package_file_path = os.path.join(
                self.temp_dir,
                "downloaded_file"
            )
            with open(package_file_path, "wb") as file:
                file.write(file_data)
            logging.info("File downloaded successfully.")
        else:
            raise ConnectionError("Failed to download the file.")

    def clone_repo(self, repo_url):
        repo = repo_url[0]
        try:
            subprocess.run(
                ["git", "clone", repo, self.temp_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            # Here should clone base on version. Check GoLang
            logging.info(f"Repository cloned successfully to {self.temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            # shutil.rmtree(self.temp_dir)
            raise
