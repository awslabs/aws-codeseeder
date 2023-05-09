#  Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License").
#    You may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
from io import open
from typing import Dict

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
about: Dict[str, str] = {}
path = os.path.join(here, "aws_codeseeder", "__metadata__.py")
with open(file=path, mode="r", encoding="utf-8") as f:
    exec(f.read(), about)

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

with open("README.md") as fp:
    long_description = fp.read()

setup(
    name=about["__title__"],
    version=version,
    author="AWS Professional Services",
    author_email="aws-proserve-opensource@amazon.com",
    url="https://github.com/awslabs/aws-codeseeder",
    project_urls={"Org Site": "https://aws.amazon.com/professional-services/"},
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=about["__license__"],
    packages=find_packages(include=["aws_codeseeder", "aws_codeseeder.*"]),
    keywords=["aws", "cdk"],
    python_requires=">=3.7, <3.12",
    install_requires=[
        "boto3>=1.19.0",
        "pyyaml>=5.4",
        "click>=7.1.0",
        "cfn-flip>=1.2.3",
        "mypy_extensions>=0.4.3",
    ],
    extras_require={
        "modules": [
            "awscli>=1.19.0",
            "wheel>=0.38.1",
            "twine>=3.3.0",
        ]
    },
    entry_points={"console_scripts": ["codeseeder = aws_codeseeder.__main__:main"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    include_package_data=True,
)
