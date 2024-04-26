import os
import magic
import hashlib
import logging
import requests
import subprocess
from .base_handler import BaseHandler
from urllib.parse import urlparse, parse_qs
from ..common import PackageManager, temp_directory
from ..utils import download_file, temp_directory, extract_tar


class GenericHandler(BaseHandler):
    def fetch(self):
        details = self.purl_details
        qualifiers = details.get('qualifiers', {})
        download_url = qualifiers.get('download_url', [None])[0]
        vcs_url = qualifiers.get('vcs_url', [None])[0]
        checksum = qualifiers.get('checksum', [None])[0]
        with temp_directory() as temp_dir:
            self.temp_dir = temp_dir
            if download_url:
                self.download_file(download_url, checksum)
                logging.info(f"File downloaded in {self.temp_dir}")
                self.unpack()
            elif vcs_url:
                self.clone_repository(vcs_url)
                logging.info(f"Repo cloned to {self.temp_dir}")
            self.scan()

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
            self.temp_dir, ['COPYRIGHT', 'NOTICES', 'LICENSE']
        )
        results['license_files'] = files
        copyhits = PackageManager.scan_for_copyright(self.temp_dir)
        results['copyrights'] = copyhits
        self.results = results

    def generate_report(self):
        logging.info("Generating report based on the scanned data...")
        return self.results

    def verify_checksum(self, data, provided_checksum):
        if ':' in provided_checksum:
            _, provided_checksum = provided_checksum.split(':', 1)
        hash_sha256 = hashlib.sha256()
        hash_sha256.update(data)
        full_checksum = hash_sha256.hexdigest()
        return full_checksum.startswith(provided_checksum)

    def download_file(self, url, checksum=None):
        response = requests.get(url)
        if response.status_code == 200:
            file_data = response.content
            if checksum and not self.verify_checksum(file_data, checksum):
                raise ValueError("Checksum verification failed!")
            package_file_path = os.path.join(
                self.temp_dir,
                "downloaded_file"
            )
            with open(package_file_path, "wb") as file:
                file.write(file_data)
            logging.info("File downloaded successfully.")
        else:
            raise ConnectionError("Failed to download the file.")

    def clone_repository(self, vcs_url):
        try:
            decoded_url = urlparse(vcs_url)
            repo_url = decoded_url.geturl()
            if repo_url.startswith('git+'):
                repo_url = repo_url[4:]
            if '@' in repo_url:
                repo_url, commit = repo_url.rsplit('@', 1)
            else:
                commit = None
            subprocess.run(
                ["git", "clone", repo_url, self.temp_dir],
                check=True
            )
            print(f"Repository cloned successfully to {self.temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            shutil.rmtree(self.temp_dir)
            raise
