# Xmonkey Namonica
## Summary
Xmonkey Namonica (xmonkey-namonica) is a Python tool created to facilitate the generation of Open Source Legal Notices, which contain copyright and license information from Open Source packages. The main goal of the tool is to provide a tool for developers to programmatically generate legal notices for the open-source software shipped in their projects, with fewer requirements and no friction.

The tool uses a few other Xmonkey libraries under the hood, for example:
* Lidy: LiDY - Simplified License Identification Library.

## Usage

You can generate a notices file including copyright information by running the tool against a PURL or an Open Source Package Inventory (OSPI) file (for  multiple PURLs):

```
$xmonkey-namonica "pkg:{ecosystem}/[{namespace}/]{component_name}@{version}[?{qualifier}={value}]"
```

```
$xmonkey-namonica ospi.txt
```

### Advanced Options
```
options:
  --export EXPORT  Path to export the output to a file
  --full           Print a full list of copyrights and license files
  --ospi           Print a list of PURLs and Licenses
```

## Package URL (purl)
PURL is a single URL parameter that uses a common industry standard structure to identify a package (Software). See the [PURL Spec](https://github.com/package-url/purl-spec) project for details on the specification's structure. In some cases, xmonkey-namonica may deviate from the purl spec standard to precisely identify components used in your application, like when you must submit a Compliance Tarball for Copyleft licenses.

```
"pkg:{ecosystem}/[{namespace}/]{component_name}@{version}[?{qualifier}={value}]"
```

### generic
A generic PURL is useful to handle cases where packages are build from source or where we must provide source compliance, as it allow recipients of the notices to obtain a copy of the software for validation. Please note that while the checksum is not needed, it's highly recommended to validate the files integrity after downloaded.

Sample generic purl is provided below:

```
xmonkey-namonica "pkg:generic/bitwarderl?vcs_url=git%2Bhttps://git.fsfe.org/dxtr/bitwarderl%40cc55108da32"
xmonkey-namonica "pkg:generic/openssl@1.1.10g?download_url=https://openssl.org/source/openssl-1.1.0g.tar.gz&checksum=sha256:de4d501267da"
```

### github
Similar to generic PURLs, the github option allow us to specify a GitHub repository, and specific versions of commits.

Sample GitHub purl is provided below:

```
xmonkey-namonica "pkg:github/package-url/purl-spec@b33dda1cf4515efa8eabbbe8e9b140950805f845"
```

### npm
Sample npm purl is provided below:

```
xmonkey-namonica "pkg:npm/tslib@2.6.2/"
```

### nuget
Sample NuGet purl is provided below:

```
xmonkey-namonica "pkg:nuget/Newtonsoft.json@13.0.3"
```

### PyPI
Sample PyPI purl is provided below:

```
xmonkey-namonica "pkg:pypi/flask@3.0.3/"
```

### Cargo (RUST)
Sample Cargo purl is provided below:

```
xmonkey-namonica "pkg:cargo/grin@1.0.0?type=crate"
```

### Golang (Go)
Sample Golang purl is provided below:

```
xmonkey-namonica "pkg:golang/github.com/mailru/easyjson@v0.7.7"
```

### Gem (Ruby)
Sample Ruby purl is provided below:

```
xmonkey-namonica "pkg:gem/jruby-launcher@1.1.18?platform=java"
```

### Conda (Python Conda)
Sample Conda purl is provided below:

```
xmonkey-namonica "pkg:conda/absl-py@1.3.0?build=pyhd8ed1ab_0&channel=main&subdir=noarch"
```

### Work in Progress:
* Maven (*)
* RPM
* Conan
* Bower
* Composer
* Cran
* Cocoapods
* Swift

## Install
Before installing xmonkey-namonica, you must install some system dependencies required by the tool.

xmonkey-namonica requires Python3.8+

### Mac
LibMagic is required for mimetype detection on MacOS. Use Brew to install the library:

```
% brew install libmagic
```

### Amazon Linux 2
If you are using Amazon Linux 2, you will need to deal with old dependencies, as such you will need to enable the EPEL repository, Development Tools, and a few other libraries:

```
$ sudo amazon-linux-extras install epel -y
$ sudo yum update -y
$ sudo yum group install "Development Tools" -y
$ sudo yum install python3-devel -y
$ pip3 install --upgrade wheel
$ pip3 install --upgrade cffi
$ pip3 install xmonkey-namonica
```

## Troubleshooting

### urllib3

If you are dealing with an error similar to the one displayed below, you will need to downgrade urllib3:

```
urllib3 v2.0 only supports OpenSSL 1.1.1+, currently "
ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips  26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
```

```
$ pip3 install "urllib3<2.0"
```

### Old Python on AL2

If your system doesn't support Python 3.8+, you can upgrade to the most recent version using amazon-linux-extras:

```
$ sudo yum remove python3
$ sudo amazon-linux-extras install python3.8
$ rpm -ql python38
$ sudo ln -s /usr/bin/python3.8 /usr/bin/python3
$ sudo yum install python38-devel
$ python3 -m pip install --upgrade cffi
$ python3 -m pip install xmonkey-namonica
$ python3 -m pip install "urllib3<2.0"
```

If you still have trouble, please install Python 3.9+ from source. Here is an interesting guide that can help: https://techviewleo.com/how-to-install-python-on-amazon-linux-2/