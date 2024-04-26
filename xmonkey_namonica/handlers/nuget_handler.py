from ..utils import download_file, temp_directory, extract_zip
from ..utils import download_file, temp_directory, extract_zip
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
import os


class NugetHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        with temp_directory() as temp_dir:
            filename = (
                f"{self.purl_details['name']}-"
                f"{self.purl_details['version']}.zip"
            )
            package_file_path = os.path.join(
                temp_dir,
                filename
            )
            download_file(download_url, package_file_path)
            print(f"Downloaded NUGET package to {package_file_path}")
            self.temp_dir = temp_dir
            self.unpack()
            self.scan()

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
            print(f"Unpacked NUGET package in {self.temp_dir}")

    def scan(self):
        results = {}
        print("Scanning package contents...")
        files = PackageManager.scan_for_files(
            self.temp_dir, ['COPYRIGHT', 'NOTICES', 'LICENSE']
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
            f"https://www.nuget.org/api/v2/package/"
            f"{self.purl_details['name']}/"
            f"{self.purl_details['version']}"
        )
