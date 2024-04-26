from setuptools import setup, find_packages

setup(
    name='xmonkey_namonica',
    version='0.1.2',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xmonkey-namonica = xmonkey_namonica.cli:main'  # Changed here
        ]
    },
    install_requires=[
        # Dependencies such as 'requests', etc.
    ],
)
