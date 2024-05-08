from abc import ABC, abstractmethod
import os
import shutil
from ..common import PackageManager


class BaseHandler(ABC):
    def __init__(self, purl):
        self.purl_details = PackageManager.parse_purl(purl)
        self.temp_dir = None

    @abstractmethod
    def fetch(self):
        """Fetch the package based on the PURL details."""
        pass

    @abstractmethod
    def unpack(self):
        """Unpack the fetched package."""
        pass

    @abstractmethod
    def scan(self):
        """Scan the unpacked package for relevant data."""
        pass

    @abstractmethod
    def generate_report(self):
        """Generate a report from the scanned data."""
        pass

    @abstractmethod
    def get_license(self, pkg_name):
        """Obtain the license from repo or package metadata."""
        pass

    def cleanup(self):
        """Remove the temporary directory created for package handling."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up temporary directory: {self.temp_dir}")
