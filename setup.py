"""Setup.py module for the aac-req-qa plugin."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-project, and it won't be overwritten if the file already exists.

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    readme_description = fh.read()

runtime_dependencies = [
    "aac ~= 0.4.8",
    "openai ~= 1.30.5",
]

test_dependencies = [
    "build>=1.0.0",
    "tox >= 3.24",
    "nose2 ~= 0.10.0",
    "coverage ~= 6.0",
    "flake8 ~= 4.0",
    "flake8-docstrings ~= 1.6.0",
    "flake8-fixme ~= 1.1.1",
    "flake8-eradicate ~= 1.2.0",
    "flake8-assertive ~= 1.3.0",
]

setup(
    version="0.2.7",
    name="aac-req-qa",
    license="MIT License",
    url="https://github.com/DevOps-MBSE/AaC-Req-QA",
    long_description=readme_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={"": ["*.aac", "*.jinja2", "*.yaml"]},
    install_requires=runtime_dependencies,
    setup_requires=test_dependencies,
    tests_require=test_dependencies,
    extras_require={"test": test_dependencies},
    entry_points={
        "aac": ["eval-req=aac_req_qa"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    keywords=["MBSE", "Requirements", "QA"],
)
