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

import random
import string
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from aws_codeseeder import LOGGER
from aws_codeseeder.services import cloudwatch, codebuild, s3


def _print_codebuild_logs(
    events: List[cloudwatch.CloudWatchEvent],
    codebuild_log_callback: Optional[Callable[[str], None]] = None,
) -> None:
    for event in events:
        msg = event.message[:-1] if event.message.endswith("\n") else event.message
        LOGGER.debug("[CODEBUILD] %s", msg)
        if codebuild_log_callback:
            codebuild_log_callback(msg)


def _wait_execution(
    build_id: str,
    stream_name_prefix: str,
    codebuild_log_callback: Optional[Callable[[str], None]] = None,
) -> None:
    start_time: Optional[datetime] = None
    stream_name: Optional[str] = None
    for status in codebuild.wait(build_id=build_id):
        if status.logs.enabled and status.logs.group_name:
            if stream_name is None:
                stream_name = cloudwatch.get_stream_name_by_prefix(
                    group_name=status.logs.group_name,
                    prefix=f"{stream_name_prefix}/",
                )
            if stream_name is not None:
                events = cloudwatch.get_log_events(
                    group_name=status.logs.group_name,
                    stream_name=stream_name,
                    start_time=start_time,
                )
                _print_codebuild_logs(events=events.events, codebuild_log_callback=codebuild_log_callback)
                if events.last_timestamp is not None:
                    start_time = events.last_timestamp + timedelta(milliseconds=1)


def _execute_codebuild(
    stack_outputs: Dict[str, str],
    bundle_location: str,
    execution_id: str,
    buildspec: codebuild.SPEC_TYPE,
    timeout: int,
    overrides: Optional[Dict[str, Any]] = None,
    codebuild_log_callback: Optional[Callable[[str], None]] = None,
) -> None:
    LOGGER.debug("bundle_location: %s", bundle_location)
    stream_name_prefix = f"codeseeder-{execution_id}"
    LOGGER.debug("stream_name_prefix: %s", stream_name_prefix)
    build_id = codebuild.start(
        project_name=stack_outputs["CodeBuildProject"],
        stream_name=stream_name_prefix,
        bundle_location=bundle_location,
        buildspec=buildspec,
        timeout=timeout,
        overrides=overrides,
    )
    _wait_execution(
        build_id=build_id,
        stream_name_prefix=stream_name_prefix,
        codebuild_log_callback=codebuild_log_callback,
    )


def run(
    stack_outputs: Dict[str, str],
    bundle_path: str,
    buildspec: codebuild.SPEC_TYPE,
    timeout: int,
    overrides: Optional[Dict[str, Any]] = None,
    codebuild_log_callback: Optional[Callable[[str], None]] = None,
) -> None:
    execution_id = "".join(random.choice(string.ascii_lowercase) for i in range(8))
    key: str = f"codeseeder/{execution_id}/bundle.zip"
    bucket = stack_outputs["Bucket"]
    s3.delete_objects(bucket=bucket, keys=[key])
    s3.upload_file(src=bundle_path, bucket=bucket, key=key)
    _execute_codebuild(
        stack_outputs=stack_outputs,
        bundle_location=f"{bucket}/{key}",
        execution_id=execution_id,
        buildspec=buildspec,
        codebuild_log_callback=codebuild_log_callback,
        timeout=timeout,
        overrides=overrides,
    )
    s3.delete_objects(bucket=bucket, keys=[key])
