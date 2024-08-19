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

import datetime as dt
import os

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws
from moto.core.utils import unix_time_millis

from aws_codeseeder.services import _utils, cfn, cloudwatch, codebuild, s3


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
    with mock_aws():
        yield _utils.boto3_client(service_name="cloudformation", session=None)


@pytest.fixture(scope="function")
def s3_client(aws_credentials):
    with mock_aws():
        yield _utils.boto3_client(service_name="s3", session=None)


@pytest.fixture(scope="function")
def logs_client(aws_credentials):
    with mock_aws():
        yield _utils.boto3_client(service_name="logs", session=None)


@pytest.fixture(scope="function")
def codebuild_client(aws_credentials):
    with mock_aws():
        yield _utils.boto3_client(service_name="codebuild", session=None)


@pytest.fixture(scope="function")
def sts_client(aws_credentials):
    with mock_aws():
        yield _utils.boto3_client(service_name="sts", session=None)


@pytest.fixture(scope="function")
def test_bucket(s3_client):
    bucket_name = "test-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.upload_file(Filename="README.md", Bucket=bucket_name, Key="fixtures/00-README.md")
    s3_client.upload_file(Filename="README.md", Bucket=bucket_name, Key="fixtures/01-README.md")
    s3_client.upload_file(Filename="README.md", Bucket=bucket_name, Key="fixtures/02-README.md")
    return bucket_name


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_utils_boto3_client(aws_credentials, session):
    _utils.boto3_client("s3", session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_utils_boto3_resource(aws_credentials, session):
    _utils.boto3_resource("s3", session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_utils_get_region(sts_client, session):
    assert _utils.get_region(session) == "us-east-1"


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_utils_get_account_id(sts_client, session):
    account_id, arn, partition = _utils.get_sts_info(session)
    assert account_id == "123456789012"


@pytest.mark.parametrize("test_args", [{}, {"key": "value"}])
def test_utils_try_it(test_args):
    def good_callable(**kwargs):
        return "test-return"

    def bad_callable(**kwargs):
        raise ValueError("test-bad-value")

    assert _utils.try_it(f=good_callable, ex=Exception, kwargs=test_args) == "test-return"
    with pytest.raises(ValueError):
        _utils.try_it(f=bad_callable, ex=ValueError, kwargs=test_args)


def test_get_stack_name():
    assert cfn.get_stack_name(seedkit_name="test-seedkit") == "aws-codeseeder-test-seedkit"


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_get_stack_status_fails(cloudformation_client, session):
    with pytest.raises(ClientError):
        cfn.get_stack_status(stack_name="test-stack", session=session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_get_stack_status_successful(cloudformation_client, session):
    cloudformation_client.create_stack(StackName="test-stack", TemplateBody="{Resources:[]}")
    result = cfn.get_stack_status(stack_name="test-stack", session=session)
    assert result == "CREATE_COMPLETE"


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_does_stack_not_exist(cloudformation_client, session):
    result = cfn.does_stack_exist("test-stack", session=session)
    assert not result[0]


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_does_stack_exist(cloudformation_client, session):
    cloudformation_client.create_stack(StackName="test-stack", TemplateBody="{Resources:[]}")
    result = cfn.does_stack_exist("test-stack", session=session)
    assert result[0]


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_deploy_template(cloudformation_client, s3_client, test_bucket, session):
    with open("test-template.json", "w") as template_file:
        template_file.write("{Resources:[]}")

    cfn.deploy_template(stack_name="test-stack", filename="test-template.json", session=session)
    os.remove("test-template.json")

    with open("large-test-template.json", "w") as template_file:
        template_file.write("{Resources:[]}".ljust(51_201))

    with pytest.raises(ValueError):
        cfn.deploy_template(stack_name="large-test-stack", filename="large-test-template.json", session=session)

    cfn.deploy_template(
        stack_name="large-test-stack", filename="large-test-template.json", s3_bucket=test_bucket, session=session
    )
    os.remove("large-test-template.json")


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cfn_destroy_stack(cloudformation_client, session):
    cfn.destroy_stack(stack_name="test-stack", session=session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_stream_name_by_prefix_fails(logs_client, session):
    with pytest.raises(ClientError) as e:
        cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream", session=session)
    assert "ResourceNotFoundException" in str(e)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_stream_name_by_prefix_not_found(logs_client, session):
    logs_client.create_log_group(logGroupName="test-group")
    result = cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream", session=session)
    assert result is None


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_stream_name_by_prefix(logs_client, session):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    result = cloudwatch.get_stream_name_by_prefix(group_name="test-group", prefix="test-stream", session=session)
    assert result == "test-stream-0"


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_log_events_fails(logs_client, session):
    with pytest.raises(ClientError) as e:
        cloudwatch.get_log_events(
            group_name="test-group", stream_name="test-stream-0", start_time=None, session=session
        )
    assert "ResourceNotFoundException" in str(e)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_log_events_not_found(logs_client, session):
    logs_client.create_log_group(logGroupName="test-group")
    with pytest.raises(ClientError) as e:
        cloudwatch.get_log_events(
            group_name="test-group", stream_name="test-stream-0", start_time=None, session=session
        )
    assert "ResourceNotFoundException" in str(e)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_log_events_no_events(logs_client, session):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    events = cloudwatch.get_log_events(
        group_name="test-group", stream_name="test-stream-0", start_time=None, session=session
    )
    assert events.group_name == "test-group"
    assert events.stream_name_prefix == "test-stream-0"
    assert len(events.events) == 0


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_cloudwatch_get_log_events(logs_client, session):
    logs_client.create_log_group(logGroupName="test-group")
    logs_client.create_log_stream(logGroupName="test-group", logStreamName="test-stream-0")
    logs_client.put_log_events(
        logGroupName="test-group",
        logStreamName="test-stream-0",
        logEvents=[
            {"timestamp": int(unix_time_millis(dt.datetime.now(dt.timezone.utc))), "message": "test-message-0"},
            {"timestamp": int(unix_time_millis(dt.datetime.now(dt.timezone.utc))), "message": "test-message-1"},
            {"timestamp": int(unix_time_millis(dt.datetime.now(dt.timezone.utc))), "message": "test-message-2"},
            {"timestamp": int(unix_time_millis(dt.datetime.now(dt.timezone.utc))), "message": "test-message-3"},
            {"timestamp": int(unix_time_millis(dt.datetime.now(dt.timezone.utc))), "message": "test-message-4"},
        ],
    )
    events = cloudwatch.get_log_events(
        group_name="test-group", stream_name="test-stream-0", start_time=None, session=session
    )
    assert events.group_name == "test-group"
    assert events.stream_name_prefix == "test-stream-0"
    assert len(events.events) == 5


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_codebuild_start(codebuild_client, session):
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
        project_name="test-project",
        stream_name="test-stream-0",
        bundle_location="",
        buildspec={},
        timeout=5,
        session=session,
    )
    assert build_id.startswith("test-project:")

    for status in codebuild.wait(build_id=build_id, session=session):
        assert status.status.value == "SUCCEEDED"


def test_codebuild_generate_spec():
    spec = codebuild.generate_spec(
        stack_outputs={},
        cmds_install=["cmd"],
        cmds_pre=["cmd"],
        cmds_build=["cmd"],
        cmds_post=["cmd"],
        env_vars={"VAR": "value"},
        exported_env_vars=["VAR"],
        runtime_versions={"python": "3.9"},
    )
    assert spec["version"] == 0.2


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_list_keys(s3_client, test_bucket, session):
    keys = s3.list_keys(bucket=test_bucket, session=session)
    assert len(keys) == 3


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_delete_objects(s3_client, test_bucket, session):
    s3.delete_objects(bucket=test_bucket, keys=["fixtures/00-README.md", "fixtures/01-README.md"])
    keys = s3.list_keys(bucket=test_bucket, session=session)
    assert len(keys) in [1, 2]

    s3.delete_objects(bucket=test_bucket)
    keys = s3.list_keys(bucket=test_bucket, session=session)
    assert len(keys) == 0


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_delete_bucket(s3_client, test_bucket, session):
    s3.delete_bucket(bucket="no-such-bucket", session=session)
    s3.delete_bucket(bucket=test_bucket, session=session)
    assert s3_client.list_buckets()["Buckets"] == []


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_upload_file(s3_client, test_bucket, session):
    s3.upload_file(src="README.md", bucket=test_bucket, key="tests/00-README.md")
    keys = s3.list_keys(bucket=test_bucket, session=session)
    assert len(keys) == 4


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_list_s3_objects(s3_client, test_bucket, session):
    s3.upload_file(src="README.md", bucket=test_bucket, key="tests/00-README.md")
    keys = s3.list_s3_objects(bucket=test_bucket, prefix="fixtures/", session=session)
    assert len(keys["Contents"]) == 3


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_delete_bucket_by_prefix(s3_client, test_bucket, session):
    s3.delete_bucket_by_prefix(prefix="test-", session=session)
    assert s3_client.list_buckets()["Buckets"] == []


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_object_exists(s3_client, test_bucket, session):
    assert s3.object_exists(bucket=test_bucket, key="fixtures/00-README.md", session=session)
    assert not s3.object_exists(bucket=test_bucket, key="fixtures/04-README.md", session=session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_bucket_empty(s3_client, test_bucket, session):
    assert not s3.is_bucket_empty(bucket=test_bucket, folder="fixtures", session=session)


@pytest.mark.parametrize("session", [None, boto3.Session, boto3.Session()])
def test_s3_copy_object(s3_client, test_bucket, session):
    s3.copy_s3_object(
        src_bucket=test_bucket,
        src_key="fixtures/00-README.md",
        dest_bucket=test_bucket,
        dest_key="fixtures/TEST-README.md",
    )
