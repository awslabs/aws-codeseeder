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
from typing import MutableSet, Optional

import pkg_resources

from aws_codeseeder.__metadata__ import __description__, __license__, __title__
from aws_codeseeder._classes import EnvVar, EnvVarType

__all__ = ["EnvVar", "EnvVarType"]

__version__: str = pkg_resources.get_distribution(__title__).version

LOGGER: logging.Logger = logging.getLogger(__name__)

CLI_ROOT = os.path.dirname(os.path.abspath(__file__))
"""Absolute path of the CLI's directory

This directory is used internally to locate resource files included in the wheel
"""

BUNDLE_ROOT = os.path.abspath(
    os.path.join(os.environ.get("CODEBUILD_SRC_DIR", os.path.join(os.getcwd(), "codeseeder.out")), "bundle")
)
"""Absolute path of the bundled files within CodeBuild

This global is provided to consumers to simplify locating, within CodeBuild, the bundled files/directories
"""

BUNDLE_IGNORED_FILE_PATHS: MutableSet[str] = {
    "/build/",
    "/.mypy_cache/",
    ".egg-info",
    "__pycache__",
    "/codeseeder.out/",
    "/dist/",
    "/node_modules/",
    "/cdk.out/",
}
"""File path segments that cause exclusion during bundling

These file path segments are checked against files during bundling. If found in the file's path, the file is
ignored and excluded from the bundle created and submitted to CodeBuild.
"""


__all__ = [
    "__description__",
    "__license__",
    "__title__",
    "__version__",
    "EnvVar",
    "EnvVarType",
    "LOGGER",
    "CLI_ROOT",
    "BUNDLE_ROOT",
    "BUNDLE_IGNORED_FILE_PATHS",
]


def create_output_dir(name: str) -> str:
    """Helper function for creating or clearing a codeseeder.out output directory

    Parameters
    ----------
    name : str
        Name of the directory to create in  the codeseeder.out directory

    Returns
    -------
    str
        Full path of the created directory
    """
    out_dir = os.path.join(os.getcwd(), "codeseeder.out", name)
    try:
        shutil.rmtree(out_dir)
    except FileNotFoundError:
        pass
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def get_logger(level: int, format: Optional[str] = None) -> logging.Logger:
    """Helper function set LOG_LEVEL and optional log FORMAT

    Parameters
    ----------
    level : int
        logger.LOG_LEVEL
    format : Optional[str], optional
        Optional string format to apply to log lines, by default None
    """
    kwargs = {"level": level}
    if format:
        kwargs["format"] = format  # type: ignore
    logging.basicConfig(**kwargs)  # type: ignore
    LOGGER.setLevel(level=level)

    # Force loggers on dependencies to ERROR
    logging.getLogger("boto3").setLevel(logging.ERROR)
    logging.getLogger("botocore").setLevel(logging.ERROR)
    logging.getLogger("s3transfer").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

    return LOGGER
