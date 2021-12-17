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

setup(
    name=about["__title__"],
    version=version,
    author="AWS Professional Services",
    author_email="aws-proserve-opensource@amazon.com",
    url="https://github.com/awslabs/aws-codeseeder",
    project_urls={"Org Site": "https://aws.amazon.com/professional-services/"},
    description=about["__description__"],
    license=about["__license__"],
    packages=find_packages(include=["aws_codeseeder", "aws_codeseeder.*"]),
    keywords=["aws", "cdk"],
    python_requires=">=3.7, <3.9",
    install_requires=[
        "boto3>=1.19.0",
        "pyyaml>=5.4",
        "click>=7.1.0",
        "cfn-flip>=1.2.3",
        "mypy_extensions>=0.4.3",
        "wheel>=0.36.0",
        "twine>=3.3.0",
    ],
    extras_require={"modules": [f"awscli>=1.19.0"]},
    entry_points={"console_scripts": ["codeseeder = aws_codeseeder.__main__:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Jupyter",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
    ],
    include_package_data=True,
)
