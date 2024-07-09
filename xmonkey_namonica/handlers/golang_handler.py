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
from ..utils import download_file, temp_directory, check_and_extract
from ..utils import extract_zip, extract_tar, extract_bz2


class GolangHandler(BaseHandler):
    def fetch(self):
        self.base_url = "https://github.com/"
        repo_url = self.construct_repo_url()
        self.repo_url = repo_url
        with temp_directory() as temp_dir:
            self.temp_dir = temp_dir
            if "goproxy" in self.repo_url[0]:
                response = self.fetch_file(repo_url[0])
                if response == 200:
                    logging.info(f"File downloaded in {self.temp_dir}")
                    self.unpack()
                    self.scan()
                else:
                    logging.info(f"URL {repo_url[0]} not supported")
                    exit()
            elif "github" in self.repo_url[0]:
                self.clone_repo(repo_url)
                logging.info(f"Repo cloned to {self.temp_dir}")
                self.scan()
            else:
                logging.info(f"URL {repo_url[0]} not supported")
                exit()

    def placehldr(self):
        results = {}
        logging.info("Placeholder results...")
        results['license_files'] = {}
        results['copyrights'] = {}
        results['license'] = 'HTTP-404'
        results['url'] = self.repo_url
        self.results = results

    def find_github_links(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            github_links = [
                link['href'] for link in links if 'github.com' in link['href']
            ]
            if github_links:
                gh_link = github_links[0]
                parts = gh_link.split('/')
                if 'tree' in parts:
                    index = parts.index('tree')
                    parts = parts[:index]
                    return '/'.join(parts)
                else:
                    return gh_link
            else:
                return ''
        except requests.RequestException as e:
            logging.error(f"An error occurred while accessing the URL: {e}")
            exit()

    def construct_repo_url(self):
        GOLANG_REPOS = {
            "cloud.google.com/go": "googleapis/google-cloud-go",
            "go.mongodb.org/mongo-driver": "mongodb/mongo-go-driver",
            "google.golang.org/grpc": "grpc/grpc-go",
            "golang.org/x/tools": "golang/tools",
            "golang.org/x/net": "golang/net",
            "golang.org/x/sys": "golang/sys",
            "golang.org/x/text": "golang/text",
            "golang.org/x/crypto": "golang/crypto",
            "k8s.io/kubernetes": "kubernetes/kubernetes",
            "k8s.io/client-go": "kubernetes/client-go",
            "go.opentelemetry.io/contrib": "open-telemetry/opentelemetry-go",
            "github.com": (
                self.base_url + self.purl_details['fullparts'][2] + "/"
            )
        }
        base_url = "https://goproxy.io"
        go_pkg = "/".join(self.purl_details['fullparts']).replace(
            'golang/', ''
        )
        if "@" in go_pkg:
            go_pkg, version = go_pkg.split("@")
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
                'Gecko/20100101 Firefox/106.0'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        # Check if pkg exist
        versions_url = f"{base_url}/{go_pkg}/@v/list"
        response = requests.get(versions_url, headers=headers)
        if response.status_code == 403:
            print(versions_url)
            exit()
        elif response.status_code == 200:
            versions = response.text.split()
            versions.sort()
            latest_version = versions[-1]
            # If exist, and version attempt to download:
            if version:
                tarball_url = f"{base_url}/{go_pkg}/@v/{version}.zip"
                response = requests.get(tarball_url, headers=headers)
                # If fail, goes to latest
                if response.status_code != 200:
                    logging.info(f"Using {version} instead")
                    version = latest_version
                    tarball_url = f"{base_url}/{go_pkg}/@v/{version}.zip"
            else:
                logging.info(f"No version, using {version} instead")
                version = latest_version
                tarball_url = f"{base_url}/{go_pkg}/@v/{version}.zip"
            full_url = tarball_url
        else:
            logging.info(f"No version available for {go_pkg}")
            namespace = self.purl_details['namespace']
            pkg_full = self.purl_details['fullparts'][2]
            namespace = f"{namespace}/{pkg_full}"
            if namespace in GOLANG_REPOS:
                base_url = GOLANG_REPOS[namespace]
                full_url = f"https://github.com/{base_url}"
            elif "github" in namespace:
                full_url = f"https://{namespace}/{self.purl_details['name']}"
            else:
                full_url = f"https://{namespace}/{self.purl_details['name']}"
                full_url = self.find_github_links(full_url)
                full_url = f"{full_url}.git"
        return f"{full_url}", version

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
            elif 'zip' in mimetype:
                extract_zip(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'tar' in mimetype:
                extract_tar(package_file_path, self.temp_dir)
                logging.info(f"Unpacked package in {self.temp_dir}")
            elif 'bzip2' in mimetype:
                extract_bz2(package_file_path, self.temp_dir)
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
        self.results = results
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
        if "proxy" in repo_url:
            info_url = repo_url.replace('.zip', '.info')
            license_files = self.results['license_files']
            if len(license_files) == 1:
                license_file = license_files[0]
                return license_file['spdx']
            else:
                return ''
        else:
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
                logging.error("Failed: HTTP {response.status_code}")
                return ''

    def fetch_file(self, url):
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) '
                'Gecko/20100101 Firefox/106.0'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.content
            package_file_path = os.path.join(
                self.temp_dir,
                "downloaded_file"
            )
            with open(package_file_path, "wb") as file:
                file.write(file_data)
            logging.info("File downloaded successfully.")
        return response.status_code

    def clone_repo(self, repo_url):
        repo = repo_url[0]
        try:
            subprocess.run(
                ["git", "clone", repo, self.temp_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if 'latest' in self.purl_details['version']:
                self.purl_details['version'] = None
            if self.purl_details['version']:
                version = self.purl_details['version']
                try:
                    subprocess.run(
                        ["git", "-C", self.temp_dir, "checkout", version],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                except subprocess.CalledProcessError:
                    logging.warning(
                        f"Failed to checkout version {version}, "
                        f"defaulting to master/main"
                    )
            logging.info(f"Repository cloned successfully to {self.temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            raise
