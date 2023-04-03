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

import pytest

from aws_codeseeder.commands import _module_commands


def test_deploy_modules_seedkit_stack_not_exists(mocker, caplog):
    mocker.patch("aws_codeseeder.commands._module_commands.seedkit_deployed", return_value=(False, "", {}))
    _module_commands.deploy_modules(seedkit_name="test-seedkit", python_modules=["module:module-dir"])
    assert "Seedkit/Stack does not exist" in caplog.text


def test_deploy_modules_no_codeartifact(mocker, caplog):
    mocker.patch("aws_codeseeder.commands._module_commands.seedkit_deployed", return_value=(True, "", {}))
    _module_commands.deploy_modules(seedkit_name="test-seedkit", python_modules=["module:module-dir"])
    assert "CodeArtifact Repository/Domain was not deployed with the Seedkit" in caplog.text


def test_deploy_modules_bad_modules_value(mocker):
    mocker.patch(
        "aws_codeseeder.commands._module_commands.seedkit_deployed",
        return_value=(True, "", {"CodeArtifactDomain": "domain", "CodeArtifactRepository": "repository"}),
    )
    with pytest.raises(ValueError) as e:
        _module_commands.deploy_modules(seedkit_name="test-seedkit", python_modules=["module-module.dir"])
    assert "Invalid `python_module`. Modules are identified with '[package-name]:[directory]'" in str(e)


def test_deploy_modules(mocker):
    mocker.patch(
        "aws_codeseeder.commands._module_commands.seedkit_deployed",
        return_value=(True, "", {"CodeArtifactDomain": "domain", "CodeArtifactRepository": "repository"}),
    )
    mocker.patch("aws_codeseeder.commands._module_commands._bundle.generate_dir", return_value=None)
    mocker.patch("aws_codeseeder.commands._module_commands.subprocess.check_call", return_value=None)
    _module_commands.deploy_modules(seedkit_name="test-seedkit", python_modules=["module:module-dir"])
