#!/bin/bash
rm -rf dist/* build/*
#pip3 uninstall xmonkey-curator -y
#rm -rf /opt/homebrew/lib/python3.12/site-packages/xmonkey_curator/
python3 setup.py sdist bdist_wheel > scripts/build.log
pip3 uninstall xmonkey-namonica -y > scripts/install.log
rm -rf /opt/homebrew/lib/python3.12/site-packages/xmonkey_namonica/ >> scripts/install.log
pip3 install dist/xmonkey_namonica-*-py3-none-any.whl >> scripts/install.log
# pandoc --from=markdown --to=rst --output=README README.md >> scripts/install.log
# python3 -m twine upload --repository pypi dist/*
