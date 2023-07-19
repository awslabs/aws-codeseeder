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

from aws_codeseeder.commands import _seedkit_commands


def test_seedkit_not_deployed(mocker):
    mocker.patch("aws_codeseeder.services.cfn.does_stack_exist", return_value=(False, {}))
    stack_exists, stack_name, stack_outputs = _seedkit_commands.seedkit_deployed(seedkit_name="test-seedkit")
    assert not stack_exists


def test_deploy_seedkit(mocker):
    mocker.patch("aws_codeseeder.services.cfn.does_stack_exist", return_value=(False, {}))
    mocker.patch("aws_codeseeder.services.cfn.deploy_template", return_value=None)
    mocker.patch("aws_codeseeder._cfn_seedkit.get_sts_info", return_value=("123456789012", "arn:aws::::", "aws"))
    mocker.patch("aws_codeseeder._cfn_seedkit.get_region", return_value="us-east-1")
    _seedkit_commands.deploy_seedkit("test-seedkit")


def test_seedkit_deployed(mocker):
    mocker.patch("aws_codeseeder.services.cfn.does_stack_exist", return_value=(True, {}))
    stack_exists, stack_name, stack_outputs = _seedkit_commands.seedkit_deployed(seedkit_name="test-seedkit")
    assert stack_exists


def test_destroy_seedkit(mocker):
    mocker.patch("aws_codeseeder.services.cfn.does_stack_exist", return_value=(True, {}))
    mocker.patch("aws_codeseeder.services.s3.delete_bucket", return_value=None)
    mocker.patch("aws_codeseeder.services.cfn.destroy_stack", return_value=None)
    _seedkit_commands.destroy_seedkit(seedkit_name="test-seedkit")
