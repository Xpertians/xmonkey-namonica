from ..utils import download_file, temp_directory, extract_tar
from ..utils import download_file, temp_directory, extract_tar
from .base_handler import BaseHandler
from ..common import PackageManager, temp_directory
import os

class NpmHandler(BaseHandler):
    def fetch(self):
        download_url = self.construct_download_url()
        with temp_directory() as temp_dir:
            package_file_path = os.path.join(temp_dir, f"{self.purl_details['name']}-{self.purl_details['version']}.tgz")
            download_file(download_url, package_file_path)
            print(f"Downloaded NPM package to {package_file_path}")
            self.temp_dir = temp_dir
            self.unpack()
            self.scan()

    def unpack(self):
        if self.temp_dir:
            package_file_path = os.path.join(self.temp_dir, f"{self.purl_details['name']}-{self.purl_details['version']}.tgz")
            extract_tar(package_file_path, self.temp_dir)
            print(f"Unpacked NPM package in {self.temp_dir}")

    def scan(self):
        results = {}
        print("Scanning package contents...")
        files = PackageManager.scan_for_files(self.temp_dir, ['.txt', '.md', 'LICENSE'])
        license_files = PackageManager.serialize_output(files)
        results['license_files'] = license_files
        copyhits = PackageManager.scan_for_copyright(self.temp_dir)
        copyrights = PackageManager.serialize_output(copyhits)
        results['copyrights'] = copyrights
        return results

    def generate_report(self):
        print("Generating report based on the scanned data...")
        return {"status": "Report generated"}

    def construct_download_url(self):
        namespace = self.purl_details['namespace'].replace('%40', '@') if self.purl_details['namespace'] else self.purl_details['name']
        return f"https://registry.npmjs.org/{namespace}/-/{self.purl_details['name']}-{self.purl_details['version']}.tgz"
