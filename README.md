# xmonkey-namonica

## Supported Formats:
xmonkey-namonica "pkg:nuget/newtonsoft.json@13.0.1/" --full
xmonkey-namonica "pkg:pypi/flask@3.0.3/" --full
xmonkey-namonica "pkg:npm/tslib@2.6.2/" --full
xmonkey-namonica "pkg:generic/openssl@1.1.10g?download_url=https://openssl.org/source/openssl-1.1.0g.tar.gz&checksum=sha256:de4d501267da" --full
xmonkey-namonica "pkg:generic/bitwarderl?vcs_url=git%2Bhttps://git.fsfe.org/dxtr/bitwarderl%40cc55108da32" --full
xmonkey-namonica "pkg:github/package-url/purl-spec@b33dda1cf4515efa8eabbbe8e9b140950805f845" --full



## Package URL (purl)
A single URL parameter using a common industry standard structure. See the [PURL Spec](https://github.com/package-url/purl-spec) project for details on the specification's structure. In some cases, xmonkey-namonica may deviate from the purl spec standard to precisely identify components used in your application, like when you must submit a Compliance Tarball for Copyleft licenses.

```
"pkg:{ecosystem}/[{namespace}/]{component_name}@{version}[?{qualifier}={value}]"
```

### maven (WIP)
Sample Maven purl is provided below:

```
xmonkey-namonica "pkg:maven/commons-fileupload/commons-fileupload@1.2.2?type=jar"
```

### npm
Sample npm purl is provided below:

```
xmonkey-namonica "pkg:npm/grunt-bower-submodule@0.2.3"
```

### nuget
Sample NuGet purl is provided below:

```
xmonkey-namonica "pkg:nuget/Nirvana.MongoProvider@1.0.53"
```

### PyPI
Sample PyPI purl is provided below:

```
xmonkey-namonica "pkg:pypi/jaraco.logging@1.5?extension=whl&qualifier=py2.py3-none-any"
```


rpm
For rpm component identifiers, the following coordinates are supported:

name

version

architecture

Sample JSON for a rpm component identifier is provided below:

"componentIdentifier": {
  "format": "rpm",
  "coordinates": {
    "name": "AGReader",
    "version": "1.2-6.el6",
    "architecture": "ppc64"      
  }
}
Sample JSON for an RPM purl is provided below:

"packageUrl": "pkg:rpm/AGReader@.2-6.el6?arch=ppc64"
gem
For Gem component identifiers, the following coordinates are supported:

name

version

platform (optional)

Sample JSON for a Gem component identifier is provided below:

"componentIdentifier": {
  "format": "gem",
  "coordinates": {
    "name": "rails",
    "version": "5.0.4"
  }
}
Sample JSON for a gem purl is provided below:

"packageUrl": "pkg:gem/rails@5.0.4"
Golang
For Go component identifiers, the following coordinates are supported:

name

version

Sample JSON for a Go component identifier is provided below:

"componentIdentifier": {
  "format": "golang",
  "coordinates": {
    "name": "github.com/rs/cors",
    "version": "v1.4.0"
  }
}
Sample JSON for a Golang purl is provided below:

"packageUrl": "pkg:golang/github.com/rs/cors@v1.4.0"
Conan
For Conan component identifiers, the following coordinates are supported:

name

version

channel (optional)

owner (optional)

Sample JSON for a Conan component identifier is provided below:

"componentIdentifier": {
  "format": "conan",
  "coordinates": { 
        "channel": "", 
        "name": "libxml2", 
        "owner": "bincrafters", 
        "version": "2.9.8" 
  }
}
Sample JSON for a Conan purl is provided below:

"packageUrl": "pkg:conan/bincrafters/libxml2@2.9.8"
Conda
For Conda component identifiers, the following coordinates are supported:

name

version

channel (optional)

subdir (optional)

build (optional)

type (optional)

Sample JSON for a Conda component identifier is provided below:

"componentIdentifier": {
  "format": "conda",
  "coordinates": {
    "name": "openssl",
    "version": "1.0.2l",
    "channel": "main",
    "subdir": "linux-64",
    "build": "h077ae2c_5",
    "type": "tar.bz2"
   }
}
Sample JSON for a Conda purl is provided below:

"packageUrl": "pkg:conda/openssl@1.0.2l?channel=main&subdir=linux-64&build=h077ae2c_5&type=tar.bz2"
bower
For Bower component identifiers, the following coordinates are supported:

name

version

Sample JSON for a Bower component identifier is provided below:

"componentIdentifier": {
  "format": "bower",
  "coordinates": {
    "name": "js-yaml",
    "version": "2.0.1"
  }
}
Sample JSON for a Bower purl is provided below:

"packageUrl": "pkg:bower/js-yaml@2.0.1"
composer
For Composer component identifiers, the following coordinates are supported:

namespace

name

version

Sample JSON for a Composer component identifier is provided below:

"componentIdentifier": {
  "format": "composer",
  "coordinates": {
        "namespace": "components",
    "name": "jqueryui",
    "version": "1.11.4"
  }
}
Sample JSON for a Composer purl is provided below:

"packageUrl": "pkg:composer/components/jqueryui@1.11.4"
Cran
For Cran component identifiers, the following coordinates are supported:

name

version

type (optional)

Sample JSON for a Cran component identifier is provided below:

"componentIdentifier": {
  "format": "cran",
  "coordinates": {
    "name": "readxl",
    "version": "1.1.0",
    "type": "tar.gz"
  }
}
Sample JSON for a Cran purl is provided below:

"packageUrl": "pkg:cran/readxl@1.1.0?type=tar.gz"
cargo
For Cargo component identifiers, the following coordinates are supported:

name

version

type (optional)

Sample JSON for a Cargo component identifier is provided below:

"componentIdentifier": {
  "format": "cargo",
  "coordinates": {
    "name": "grin",
    "version": "1.0.0",
    "type": "crate"
  }
}
Sample JSON for a Cargo purl is provided below:

"packageUrl": "pkg:cargo/grin@1.0.0?type=crate"
CocoaPods
For CocoaPods component identifiers, the following coordinates are supported:

name

version

Sample JSON for a CocoaPods component identifier is provided below:

"componentIdentifier": {
  "format": "cocoapods",
  "coordinates": {
    "name": "libpng",
    "version": "1.4.9"
  }
}
Sample JSON for a CocoaPods purl is provided below:

"packageUrl": "pkg:cocoapods/libpng@1.4.9"
Drupal
For Drupal package identifiers, the following coordinates are supported:

name

version

Sample JSON for a Drupal component identifier is provided below:

"componentIdentifier": {
  "format": "drupal",
  "coordinates": {
    "name": "simplenews",
    "version": "2.0.0"
  }
}
Sample JSON for a Drupal purl is provided below:

"packageUrl": "pkg:drupal/simplenews@2.0.0"
pecoff
For Pecoff identifiers, the following coordinates are supported:

name

namespace (optional)

version

Sample JSON for a Pecoff component identifier is provided below:

"componentIdentifier": {
  "format": "pecoff",
  "coordinates": {
    "name": "0Harmony.dll",
    "namespace":"BepInEx/HarmonyX"
    "version": "2.0.0.0"
  }
}
Sample JSON for a Pecoff purl is provided below:

"packageUrl": "pkg:generic/BepInEx/HarmonyX/0Harmony.dll@2.0.0.0?nexustype=pecoff"
SINCE RELEASE 101

"pkg:generic/0Harmony.dll@2.0.0.0?nexusnamespace=BepInEx%2FHarmonyX&nexustype=pecoff"
Swift
For swift identifiers, the following coordinates are supported:

name

version

Sample JSON for a swift component identifier is provided below:

"componentIdentifier": {
  "format": "swift",
  "coordinates": {
    "name": "github.com/ReactiveX/RxSwift",
    "version": "5.1.0"
  }
}
Sample JSON for a swift purl is provided below:

"packageUrl": "pkg:swift/github.com/ReactiveX/RxSwift@5.1.0"