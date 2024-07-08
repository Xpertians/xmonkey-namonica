import os
import magic
import shutil
import hashlib
import logging
import requests
import subprocess
from .base_handler import BaseHandler
from urllib.parse import urlparse, parse_qs
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_tar


class GithubHandler(BaseHandler):
    def fetch(self):
        self.base_url = "https://github.com/"
        repo_url = self.construct_repo_url()
        self.repo_url = repo_url
        with temp_directory() as temp_dir:
            self.temp_dir = temp_dir
            if self.purl_details['subpath']:
                self.fetch_file(repo_url)
                logging.info(f"File downloaded in {self.temp_dir}")
                self.unpack()
            else:
                self.clone_repo(repo_url)
                logging.info(f"Repo cloned to {self.temp_dir}")
            self.scan()

    def construct_repo_url(self):
        namespace = self.purl_details['namespace']
        name = self.purl_details['name']
        # Default to main if no version is provided
        version = self.purl_details.get('version', 'main')
        return f"{self.base_url}{namespace}/{name}.git", version

    def unpack(self):
        if self.temp_dir:
            package_file_path = os.path.join(
                self.temp_dir,
                "downloaded_file"
            )
            mime = magic.Magic(mime=True)
            mimetype = mime.from_file(package_file_path)
            if 'gzip' in mimetype:
                extract_tar(package_file_path, self.temp_dir)
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
        results['license'] = self.get_license(self.repo_url)
        results['url'] = self.repo_url[0]
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

    def get_license(self, repo_url):
        repo_url = repo_url[0]
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        repo_path = repo_url.split("github.com/")[1]
        api_url = f"https://api.github.com/repos/{repo_path}/license"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            license_name = data.get('license', {}).get('name', '')
            return license_name
        elif response.status_code == 404:
            logging.error("License file not found in repository")
            return ''
        else:
            logging.error(
                "Failed: HTTP {response.status_code}"
            )
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
            if self.purl_details['version']:
                version = self.purl_details['version']
                subprocess.run(
                    ["git", "-C", self.temp_dir, "checkout", version],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            logging.info(f"Repository cloned successfully to {self.temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            # shutil.rmtree(self.temp_dir)
            raise
