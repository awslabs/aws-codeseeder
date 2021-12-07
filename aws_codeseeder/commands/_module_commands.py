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
import shutil
import subprocess
from typing import List, cast

from aws_codeseeder import CLI_ROOT, LOGGER, _bundle, create_output_dir
from aws_codeseeder.services import cfn

FILENAME = "update_repo.sh"
RESOURCES_FILENAME = os.path.join(CLI_ROOT, "resources", FILENAME)


def _prep_modules_directory() -> str:
    LOGGER.info("Preparing modules working directory")
    out_dir = create_output_dir("modules")
    dst_file = os.path.join(out_dir, FILENAME)
    LOGGER.debug("Copying file to %s", dst_file)
    shutil.copy(src=RESOURCES_FILENAME, dst=dst_file)

    return out_dir


def deploy_modules(seedkit_name: str, python_modules: List[str]) -> None:
    """Deploy local Python modules to the CodeArtifact Domain/Repository associated with a Seedkit

    This is a utility function that attempts to package and deploy local Python projects to CodeArtifact for use in
    CodeBuild executions.

    Parameters
    ----------
    seedkit_name : str
        Name of a previously deployed Seedkit
    python_modules : List[str]
        List of local Python modules/projects to deploy. Each module is of the form
        "[package-name]:[directory]" where [package-name] is the name of the Python package and [directory] is the
        local location of the module/project

    Raises
    ------
    ValueError
        If module names are of the wrong form
    """
    stack_name: str = cfn.get_stack_name(seedkit_name=seedkit_name)
    LOGGER.info("Deploying Modules for Seedkit %s with Stack Name %s", seedkit_name, stack_name)
    LOGGER.debug("Python Modules: %s", python_modules)

    stack_exists, stack_outputs = cfn.does_stack_exist(stack_name=stack_name)
    if not stack_exists:
        LOGGER.warn("Seedkit/Stack does not exist")
        return
    domain = stack_outputs.get("CodeArtifactDomain")
    repository = stack_outputs.get("CodeArtifactRepository")

    if any([":" not in pm for pm in python_modules]):
        raise ValueError(
            "Invalid `python_module`. Modules are identified with '[package-name]:[directory]': %s", python_modules
        )

    out_dir = _prep_modules_directory()
    modules = {ms[0]: ms[1] for ms in [m.split(":") for m in python_modules]}

    for module, dir in modules.items():
        LOGGER.info("Creating working directory for Module %s", module)
        _bundle.generate_dir(out_dir=out_dir, dir=dir, name=module)

    for module, dir in modules.items():
        LOGGER.info("Deploy Module %s to Seedkit Domain/Repository %s/%s", module, domain, repository)
        subprocess.check_call(
            [os.path.join(out_dir, FILENAME), cast(str, domain), cast(str, repository), module, module]
        )
