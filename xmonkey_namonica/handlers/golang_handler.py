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
            if "github" in self.repo_url[0]:
                print('repo:', self.repo_url[0])
                self.clone_repo(repo_url)
                logging.info(f"Repo cloned to {self.temp_dir}")
                self.scan()
            elif ".git" in self.repo_url[0]:
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
            pkggodev_links = [
                link['href'] for link in links if 'pkg.go.dev' in link['href']
            ]
            if github_links:
                for gh_link in github_links:
                    if 'go.mod' in gh_link:
                        parts = gh_link.split('/')
                        if 'tree' in parts:
                            index = parts.index('tree')
                            parts = parts[:index]
                            return '/'.join(parts)
                        else:
                            return gh_link
            elif pkggodev_links:
                pkggo_link = pkggodev_links[0]
                return self.find_github_links(pkggo_link)
            else:
                return ''
        except requests.RequestException as e:
            logging.error(f"An error occurred while accessing the URL: {e}")
            exit()

    def construct_repo_url(self):
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

        repository = self.purl_details['repository']
        namespace = self.purl_details['namespace']
        go_pkg = self.purl_details['name']
        go_version = self.purl_details['version']

        ggl_lnk = ''
        gl_x = ''

        if "golang.org" in repository and 'x' in namespace:
            gl_x = "https://go.googlesource.com/" + go_pkg
        elif "google.golang.org" in repository:
            ggl_lnk = self.get_source_from_godev(namespace, go_pkg, go_version)
        elif "golang.org" in repository:
            gl_x = self.get_source_from_godev(repository, namespace, '')
        else:
            gl_x = ''

        if "go.opentelemetry.io" in repository:
            got_lnk = self.get_source_from_godev(repository, namespace, '')
        else:
            got_lnk = ''

        GOLANG_REPOS = {
            "cloud.google.com/go": "googleapis/google-cloud-go",
            "go.mongodb.org/mongo-driver": "mongodb/mongo-go-driver",
            "k8s.io/kubernetes": "kubernetes/kubernetes",
            "k8s.io/client-go": "kubernetes/client-go",
            "golang.org": gl_x,
            "github.com": (
                "https://github.com/" + namespace + "/" + go_pkg + "/"
            )
        }

        if repository in GOLANG_REPOS:
            full_url = GOLANG_REPOS[repository]
            if "github" not in full_url:
                full_url = f"{full_url}.git"
        elif "golang.org" in repository and not "google" in repository:
            full_url = f"https://{namespace}/{self.purl_details['name']}"
            full_url = f"{full_url}.git"
        elif "go.opentelemetry.io" in repository:
            got_lnk = self.get_source_from_godev(repository, namespace, '')
            full_url = f"https://github.com/{got_lnk}"
            full_url = f"{full_url}.git"
        elif "github" in repository:
            full_url = f"https://{namespace}/{self.purl_details['name']}"
        else:
            full_url = f"https://{namespace}/{self.purl_details['name']}"
            full_url = self.find_github_links(full_url)
            full_url = f"{full_url}.git"
        print(f"{full_url}", go_version)
        return f"{full_url}", go_version

    def get_source_from_godev(self, namespace, pkg_name, pkg_version):
        try:
            base_url = f"https://pkg.go.dev/{namespace}/{pkg_name}"
            response = requests.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            version_link = soup.find('a', href=f"/{namespace}/{pkg_name}@{pkg_version}")
            if version_link is None:
                version_link = soup.find('a', href=f"/{namespace}/{pkg_name}")
            source_files_url = f"https://pkg.go.dev{version_link['href']}#section-sourcefiles"
            response = requests.get(source_files_url)
            response.raise_for_status()
            source_files_html = response.text
            soup = BeautifulSoup(source_files_html, 'html.parser')
            gh_host = 'https://github.com/'
            github_links = soup.find_all('a', href=lambda href: href.startswith(gh_host))
            github_link = ''
            for link in github_links:
                if 'go.mod' in link.get('href'):
                    gh_lnks = link.get('href').split('/')
                    github_link = gh_lnks[3]+ "/" + gh_lnks[4]
            return github_link
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

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
        elif "github.com" in repo_url:
            if repo_url.endswith('.git'):
                repo_url = repo_url[:-4]
            repo_path = repo_url.split("github.com/")[1]
            api_url = f"https://api.github.com/repos/{repo_path}/license"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                license_name = data.get('license', {}).get('name', '')
                return license_name
            else:
                api_url = f"https://api.github.com/repos/{repo_path}/COPYING"
                response = requests.get(api_url)
                if response.status_code == 200:
                    data = response.json()
                    license_name = data.get('license', {}).get('name', '')
                    return license_name
                else:
                    return ''
        else:
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
                    print(
                        f"Failed to checkout version {version}, "
                        f"defaulting to master/main"
                    )
            logging.info(f"Repository cloned successfully to {self.temp_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e}")
            raise
