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

from datetime import datetime

import pytest

from aws_codeseeder import _remote
from aws_codeseeder.services.codebuild import BuildCloudWatchLogs, BuildInfo, BuildPhaseType, BuildStatus


def test_run(mocker):
    mocker.patch("aws_codeseeder._remote.s3.delete_objects", return_value=None)
    mocker.patch("aws_codeseeder._remote.s3.upload_file", return_value=None)
    mocker.patch("aws_codeseeder._remote.codebuild.start", return_value="test-xxxxxxxx")
    mocker.patch(
        "aws_codeseeder._remote.codebuild.wait",
        return_value=[
            BuildInfo(
                build_id="test-xxxxxxxx",
                status=BuildStatus.succeeded,
                current_phase=BuildPhaseType.completed,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                duration_in_seconds=1.0,
                exported_env_vars=[],
                phases=[],
                logs=BuildCloudWatchLogs(enabled=False, group_name=None, stream_name=None),
            )
        ],
    )
    _remote.run(
        stack_outputs={"Bucket": "test-bucket", "CodeBuildProject": "test-project"},
        bundle_path=".",
        buildspec={},
        timeout=60,
    )
