from setuptools import setup, find_packages

setup(
    name='xmonkey_namonica',
    version='0.1.7',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'xmonkey-namonica = xmonkey_namonica.cli:main'
        ]
    },
    python_requires='>=3.6',
    install_requires=[
        "spacy",
        "nltk",
        "scikit-learn",
        "pandas",
        "numpy",
        "requests",
        "urllib3",
    ],
)
