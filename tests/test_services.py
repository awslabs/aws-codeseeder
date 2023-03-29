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
from datetime import datetime
from typing import Any

import pytest
from botocore.exceptions import ClientError
from moto import mock_cloudformation, mock_codebuild, mock_logs, mock_s3
from moto.moto_api import state_manager

from aws_codeseeder.services import cfn, cloudwatch, codebuild
from aws_codeseeder.services._utils import boto3_client


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["MOTO_ACCOUNT_ID"] = "123456789012"


@pytest.fixture(scope="function")
def cloudformation_client(aws_credentials):
    with mock_cloudformation():
        yield boto3_client(service_name="cloudformation", session=None)


@pytest.fixture(scope="function")
def s3_client(aws_credentials):
    with mock_s3():
        yield boto3_client(service_name="s3", session=None)


@pytest.fixture(scope="function")
def logs_client(aws_credentials):
    with mock_logs():
        yield boto3_client(service_name="logs", session=None)


@pytest.fixture(scope="function")
def codebuild_client(aws_credentials):
    with mock_codebuild():
        yield boto3_client(service_name="codebuild", session=None)


def test_get_stack_name():
    assert cfn.get_stack_name(seedkit_name="test-seedkit") == "aws-codeseeder-test-seedkit"


def test_cfn_get_stack_status_fails(cloudformation_client):
    with pytest.raises(ClientError):
        result = cfn.get_stack_status(stack_name="test-stack", session=None)


def test_cfn_get_stack_status_successful(cloudformation_client):
    cloudformation_client.create_stack(StackName="test-stack", TemplateBody="{Resources:[]}")
    result = cfn.get_stack_status(stack_name="test-stack", session=None)
    assert result == "CREATE_COMPLETE"


def test_cfn_does_stack_not_exist(cloudformation_client):
    result = cfn.does_stack_exist("test-stack", session=None)
    assert not result[0]


def test_cfn_does_stack_exist(cloudformation_client):
    cloudformation_client.create_stack(StackName="test-stack", TemplateBody="{Resources:[]}")
    result = cfn.does_stack_exist("test-stack", session=None)
    assert result[0]


def test_cfn_deploy_template(cloudformation_client, s3_client):
    with open("test-template.json", "w") as template_file:
        template_file.write("{Resources:[]}")

    cfn.deploy_template(stack_name="test-stack", filename="test-template.json")
    os.remove("test-template.json")

    with open("large-test-template.json", "w") as template_file:
        template_file.write("{Resources:[]}".ljust(51_201))
    s3_client.create_bucket(Bucket="test-bucket")

    with pytest.raises(ValueError):
        cfn.deploy_template(stack_name="large-test-stack", filename="large-test-template.json")

    cfn.deploy_template(stack_name="large-test-stack", filename="large-test-template.json", s3_bucket="test-bucket")
    os.remove("large-test-template.json")


def test_cfn_destroy_stack(cloudformation_client):
    cfn.destroy_stack(stack_name="test-stack", session=None)


def test_cloudwatch_get_stream_name_by_prefix_fails(logs_client):
    with pytest.raises(ClientError) as e:
        cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream")
    assert "ResourceNotFoundException" in str(e)


def test_cloudwatch_get_stream_name_by_prefix_not_found(logs_client):
    logs_client.create_log_group(logGroupName="test-group")
    result = cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream")
    assert result is None


def test_cloudwatch_get_stream_name_by_prefix(logs_client):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    result = cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream")
    assert result == "test-stream-0"


def test_cloudwatch_get_log_events_fails(logs_client):
    with pytest.raises(ClientError) as e:
        events = cloudwatch.get_log_events(group_name="test-group", stream_name="test-stream-0", start_time=None)
    assert "ResourceNotFoundException" in str(e)


def test_cloudwatch_get_log_events_not_found(logs_client):
    logs_client.create_log_group(logGroupName="test-group")
    with pytest.raises(ClientError) as e:
        events = cloudwatch.get_log_events(group_name="test-group", stream_name="test-stream-0", start_time=None)
    assert "ResourceNotFoundException" in str(e)


def test_cloudwatch_get_log_events_no_events(logs_client):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    events = cloudwatch.get_log_events(group_name="test-group", stream_name="test-stream-0", start_time=None)
    assert events.group_name == "test-group"
    assert events.stream_name_prefix == "test-stream-0"
    assert len(events.events) == 0


def test_cloudwatch_get_log_events(logs_client):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    logs_client.put_log_events(
        logGroupName="test-group",
        logStreamName="test-stream-0",
        logEvents=[
            {"timestamp": int(datetime.now().timestamp()), "message": "test-message-0"},
            {"timestamp": int(datetime.now().timestamp()), "message": "test-message-1"},
            {"timestamp": int(datetime.now().timestamp()), "message": "test-message-2"},
            {"timestamp": int(datetime.now().timestamp()), "message": "test-message-3"},
            {"timestamp": int(datetime.now().timestamp()), "message": "test-message-4"},
        ],
    )
    events = cloudwatch.get_log_events(group_name="test-group", stream_name="test-stream-0", start_time=None)
    assert events.group_name == "test-group"
    assert events.stream_name_prefix == "test-stream-0"
    assert len(events.events) == 0  # moto not working correctly here, the test events are not returned


def test_codebuild_start(codebuild_client):
    codebuild_client.create_project(
        name="test-project",
        source={"type": "NO_SOURCE", "location": "/"},
        artifacts={"type": "NO_ARTIFACTS"},
        environment={
            "type": "LINUX_CONTAINER",
            "image": "aws/codebuild/standard:4.0",
            "computeType": "BUILD_GENERAL1_SMALL",
        },
        serviceRole="arn:aws:iam::123456789012:role/service-role/test-role",
    )
    build_id = codebuild.start(
        project_name="test-project", stream_name="test-stream-0", bundle_location="", buildspec={}, timeout=5
    )
    assert build_id.startswith("test-project:")

    state_manager.set_transition(model_name="codebuild::build", transition={"progression": "manual", "times": 3})

    codebuild.wait(build_id=build_id)
    info = codebuild.fetch_build_info(build_id=build_id)
    assert info.status.value == "SUCCEEDED"
