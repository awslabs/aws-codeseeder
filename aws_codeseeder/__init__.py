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

import logging
import os
import shutil

import pkg_resources

from aws_codeseeder.__metadata__ import __description__, __license__, __title__  # noqa: F401

__version__: str = pkg_resources.get_distribution(__title__).version

LOGGER: logging.Logger = logging.getLogger(__name__)
CLI_ROOT = os.path.dirname(os.path.abspath(__file__))
BUNDLE_ROOT = os.path.abspath(
    os.path.join(os.environ.get("CODEBUILD_SRC_DIR", os.path.join(os.getcwd(), "codeseeder.out")), "bundle")
)


def create_output_dir(name: str) -> str:
    out_dir = os.path.join(os.getcwd(), "codeseeder.out", name)
    try:
        shutil.rmtree(out_dir)
    except FileNotFoundError:
        pass
    os.makedirs(out_dir, exist_ok=True)
    return out_dir
