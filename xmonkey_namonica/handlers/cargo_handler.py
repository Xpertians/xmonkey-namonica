from ..utils import download_file, temp_directory, extract_tar
from ..utils import download_file, temp_directory, extract_tar
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
import os


class CargoHandler(BaseHandler):
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
            print(f"Downloaded RUST package to {package_file_path}")
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
            print(f"Unpacked RUST package in {self.temp_dir}")

    def scan(self):
        results = {}
        print("Scanning package contents...")
        files = PackageManager.scan_for_files(
            self.temp_dir, ['.txt', '.md', 'LICENSE']
        )
        results['license_files'] = files
        copyhits = PackageManager.scan_for_copyright(self.temp_dir)
        results['copyrights'] = copyhits
        self.results = results

    def generate_report(self):
        print("Generating report based on the scanned data...")
        return self.results

    def construct_download_url(self):
        namespace = (
            self.purl_details['namespace'].replace('%40', '@')
            if self.purl_details['namespace']
            else self.purl_details['name']
        )
        return (
            f"https://crates.io/api/v1/crates/"
            f"{self.purl_details['name']}/"
            f"{self.purl_details['version']}/download"
        )
