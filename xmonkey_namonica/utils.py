import os
import bz2
import magic
import shutil
import requests
import logging
import zipfile
import tarfile
import tempfile
from contextlib import contextmanager


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def download_file(url, dest):
    logging.info(f"download_file {url} to {dest}")
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(dest, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        logging.info(f"Downloaded file from {url} to {dest}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to download file from {url}: {e}")
        return False


def extract_zip(file_path, extract_to):
    logging.info(f"extract_zip {file_path} to {extract_to}")
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        remove(file_path)
        logging.info(f"Extracted ZIP file {file_path} to {extract_to}")
    except zipfile.BadZipFile as e:
        logging.error(f"Failed to extract ZIP file {file_path}: {e}")
        raise


def extract_tar(file_path, extract_to):
    logging.info(f"extract_tar {file_path} to {extract_to}")
    try:
        with tarfile.open(file_path, 'r:*') as tar_ref:
            tar_ref.extractall(extract_to)
        remove(file_path)
        logging.info(f"Extracted TAR file {file_path} to {extract_to}")
    except tarfile.TarError as e:
        logging.error(f"Failed to extract TAR file {file_path}: {e}")
        raise


def extract_bz2(file_path, extract_to):
    logging.info(f"extract_bz2 {file_path} to {extract_to}")
    try:
        if not os.path.exists(extract_to):
            os.makedirs(extract_to)
        output_file_path = os.path.join(
            extract_to,
            os.path.basename(file_path).replace('.bz2', '')
        )
        with bz2.BZ2File(file_path, 'rb') as file:
            decompressed_data = file.read()
            with open(output_file_path, 'wb') as f_out:
                f_out.write(decompressed_data)
        remove(file_path)
        logging.info(f"Extracted BZ2 file {file_path} to {output_file_path}")
    except OSError as e:
        logging.error(f"Failed to extract BZ2 file {file_path}: {e}")
        raise


def recursive_extract(file_path, extract_to):
    logging.info(f"Recursive Extract {file_path} to {extract_to}")
    mime = magic.Magic(mime=True)
    mimetype = mime.from_file(file_path)
    if 'gzip' in mimetype or 'tar' in mimetype:
        extract_tar(file_path, extract_to)
    elif 'zip' in mimetype:
        extract_zip(file_path, extract_to)
    elif 'bzip2' in mimetype:
        extract_bz2(file_path, extract_to)
    else:
        raise ValueError(f"Unsupported archive format: {mimetype}")


def check_and_extract(path, extract_to):
    logging.info(f"check_and_extract {path} to {extract_to}")
    if os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                mime = magic.Magic(mime=True)
                mimetype = mime.from_file(file_path)
                if 'gzip' in mimetype:
                    extract_tar(file_path, extract_to)
                    logging.info(f"Unpacked package in {extract_to}")
                elif 'tar' in mimetype:
                    extract_tar(file_path, extract_to)
                    logging.info(f"Unpacked package in {extract_to}")
                elif 'bzip2' in mimetype:
                    extract_bz2(file_path, extract_to)
                    logging.info(f"Unpacked package in {extract_to}")
    elif os.path.isfile(path):
        recursive_extract(path, os.path.dirname(path))


def remove(path):
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


@contextmanager
def temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)
        logging.info(f"Removed temporary directory {temp_dir}")
