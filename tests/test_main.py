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
from click.testing import CliRunner

from aws_codeseeder import __main__


def test_deploy_seedkit(mocker):
    mocker.patch("aws_codeseeder.__main__.commands.deploy_seedkit", return_value=None)
    runner = CliRunner()
    result = runner.invoke(__main__.deploy, ["seedkit", "test", "--debug"])
    assert result.exit_code == 0


def test_deploy_modules(mocker):
    mocker.patch("aws_codeseeder.__main__.commands.deploy_modules", return_value=None)
    runner = CliRunner()
    result = runner.invoke(__main__.deploy, ["modules", "test", "--debug"])
    assert result.exit_code == 0


def test_destroy_seedkit(mocker):
    mocker.patch("aws_codeseeder.__main__.commands.destroy_seedkit", return_value=None)
    runner = CliRunner()
    result = runner.invoke(__main__.destroy, ["seedkit", "test", "--debug"])
    assert result.exit_code == 0
