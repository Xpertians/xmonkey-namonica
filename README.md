# xmonkey-namonica

## Package URL (purl)
A single URL parameter using a common industry standard structure. See the [PURL Spec](https://github.com/package-url/purl-spec) project for details on the specification's structure. In some cases, xmonkey-namonica may deviate from the purl spec standard to precisely identify components used in your application, like when you must submit a Compliance Tarball for Copyleft licenses.

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