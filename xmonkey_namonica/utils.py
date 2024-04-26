import os
import requests
import logging
import zipfile
import tarfile
import tempfile
import shutil
from contextlib import contextmanager


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def download_file(url, dest):
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded file from {url} to {dest}")
    except requests.RequestException as e:
        logging.error(f"Failed to download file from {url}: {e}")
        raise


def extract_zip(file_path, extract_to):
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f"Extracted ZIP file {file_path} to {extract_to}")
    except zipfile.BadZipFile as e:
        logging.error(f"Failed to extract ZIP file {file_path}: {e}")
        raise


def extract_tar(file_path, extract_to):
    try:
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_to)
        logging.info(f"Extracted TAR file {file_path} to {extract_to}")
    except tarfile.TarError as e:
        logging.error(f"Failed to extract TAR file {file_path}: {e}")
        raise


@contextmanager
def temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
        logging.info(f"Removed temporary directory {temp_dir}")
