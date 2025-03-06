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

from setuptools import find_packages, setup

setup(
    name="my-example",
    version="0.1.0",
    packages=find_packages(include=["my_example", "my_example.*"]),
    python_requires=">=3.7, <3.13",
    install_requires=[
        "aws-codeseeder",
    ],
    entry_points={"console_scripts": ["examplecli = my_example.cli:main"]},
    include_package_data=True,
)
