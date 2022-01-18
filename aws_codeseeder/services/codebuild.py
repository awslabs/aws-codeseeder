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

import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Union

import botocore.exceptions
import yaml

from aws_codeseeder import LOGGER
from aws_codeseeder.services._utils import boto3_client, try_it

_BUILD_WAIT_POLLING_DELAY: float = 5  # SECONDS


class BuildStatus(Enum):
    failed = "FAILED"
    fault = "FAULT"
    in_progress = "IN_PROGRESS"
    stopped = "STOPPED"
    succeeded = "SUCCEEDED"
    timed_out = "TIMED_OUT"


class BuildPhaseType(Enum):
    build = "BUILD"
    completed = "COMPLETED"
    download_source = "DOWNLOAD_SOURCE"
    finalizing = "FINALIZING"
    install = "INSTALL"
    post_build = "POST_BUILD"
    pre_build = "PRE_BUILD"
    provisioning = "PROVISIONING"
    queued = "QUEUED"
    submitted = "SUBMITTED"
    upload_artifacts = "UPLOAD_ARTIFACTS"


class BuildPhaseStatus(Enum):
    failed = "FAILED"
    fault = "FAULT"
    queued = "QUEUED"
    in_progress = "IN_PROGRESS"
    stopped = "STOPPED"
    succeeded = "SUCCEEDED"
    timed_out = "TIMED_OUT"


class BuildPhaseContext(NamedTuple):
    status_code: Optional[str]
    message: Optional[str]


class BuildPhase(NamedTuple):
    phase_type: BuildPhaseType
    status: Optional[BuildPhaseStatus]
    start_time: datetime
    end_time: Optional[datetime]
    duration_in_seconds: float
    contexts: List[BuildPhaseContext]


class BuildCloudWatchLogs(NamedTuple):
    enabled: bool
    group_name: Optional[str]
    stream_name: Optional[str]


class BuildInfo(NamedTuple):
    build_id: str
    status: BuildStatus
    current_phase: BuildPhaseType
    start_time: datetime
    end_time: Optional[datetime]
    duration_in_seconds: float
    phases: List[BuildPhase]
    logs: BuildCloudWatchLogs


def start(
    project_name: str,
    stream_name: str,
    bundle_location: str,
    buildspec: Dict[str, Any],
    timeout: int,
    overrides: Optional[Dict[str, Any]] = None,
) -> str:
    """Start a CodeBuild Project execution

    Parameters
    ----------
    project_name : str
        Name of the CodeBuild Project
    stream_name : str
        Name of the CloudWatch Logs Stream to read CodeBuild logs from
    bundle_location : str
        S3 Location of the zip bundle to use as Source to the CodeBuild execution
    buildspec : Dict[str, Any]
        BuildSpec to use for the CodeBuild execution
    timeout : int
        Timeout of the CodeBuild execution
    overrides : Optional[Dict[str, Any]], optional
        Additional overrides to set on the CodeBuild execution, by default None

    Returns
    -------
    str
        The CodeBuild Build/Exectuion Id
    """
    client = boto3_client("codebuild")
    credentials: Optional[str] = "SERVICE_ROLE" if overrides and overrides.get("imageOverride", None) else None
    LOGGER.debug("Credentials: %s", credentials)
    LOGGER.debug("Overrides: %s", overrides)
    build_params = {
        "projectName": project_name,
        "sourceTypeOverride": "S3",
        "sourceLocationOverride": bundle_location,
        "buildspecOverride": yaml.safe_dump(data=buildspec, sort_keys=False, indent=4),
        "timeoutInMinutesOverride": timeout,
        "privilegedModeOverride": True,
        "logsConfigOverride": {
            "cloudWatchLogs": {
                "status": "ENABLED",
                "groupName": f"/aws/codebuild/{project_name}",
                "streamName": stream_name,
            },
            "s3Logs": {"status": "DISABLED"},
        },
    }
    if credentials:
        build_params["imagePullCredentialsTypeOverride"] = credentials

    if overrides:
        build_params = {**build_params, **overrides}

    response: Dict[str, Any] = client.start_build(**build_params)
    return str(response["build"]["id"])


def fetch_build_info(build_id: str) -> BuildInfo:
    """Fetch info on a CodeBuild execution

    Parameters
    ----------
    build_id : str
        CodeBuild Execution/Build Id

    Returns
    -------
    BuildInfo
        Info on the CodeBuild execution

    Raises
    ------
    RuntimeError
        If the Build Id is not found
    """
    client = boto3_client("codebuild")
    response: Dict[str, List[Dict[str, Any]]] = try_it(
        f=client.batch_get_builds, ex=botocore.exceptions.ClientError, ids=[build_id], max_num_tries=5
    )
    if not response["builds"]:
        raise RuntimeError(f"CodeBuild build {build_id} not found.")
    build = response["builds"][0]
    now = datetime.now(timezone.utc)
    log_enabled = True if build.get("logs", {}).get("cloudWatchLogs", {}).get("status") == "ENABLED" else False
    return BuildInfo(
        build_id=build_id,
        status=BuildStatus(value=build["buildStatus"]),
        current_phase=BuildPhaseType(value=build["currentPhase"]),
        start_time=build["startTime"],
        end_time=build.get("endTime", now),
        duration_in_seconds=(build.get("endTime", now) - build["startTime"]).total_seconds(),
        phases=[
            BuildPhase(
                phase_type=BuildPhaseType(value=p["phaseType"]),
                status=None if "phaseStatus" not in p else BuildPhaseStatus(value=p["phaseStatus"]),
                start_time=p["startTime"],
                end_time=p.get("endTime", now),
                duration_in_seconds=p.get("durationInSeconds"),
                contexts=[
                    BuildPhaseContext(status_code=p.get("statusCode"), message=p.get("message"))
                    for c in p.get("contexts", [])
                ],
            )
            for p in build["phases"]
        ],
        logs=BuildCloudWatchLogs(
            enabled=log_enabled,
            group_name=build["logs"]["cloudWatchLogs"].get("groupName") if log_enabled else None,
            stream_name=build["logs"]["cloudWatchLogs"].get("streamName") if log_enabled else None,
        ),
    )


def wait(build_id: str) -> Iterable[BuildInfo]:
    """Wait for completion of a CodeBuild execution

    Parameters
    ----------
    build_id : str
        The CodeBuild Execution/Build Id

    Returns
    -------
    Iterable[BuildInfo]
        Info on the CodeBuild execution

    Yields
    -------
    Iterator[Iterable[BuildInfo]]
        Info on the CodeBuild execution

    Raises
    ------
    RuntimeError
        If the CodeBuild doesn't succeed
    """
    build = fetch_build_info(build_id=build_id)
    while build.status is BuildStatus.in_progress:
        time.sleep(_BUILD_WAIT_POLLING_DELAY)

        last_phase = build.current_phase
        last_status = build.status
        build = fetch_build_info(build_id=build_id)

        if build.current_phase is not last_phase or build.status is not last_status:
            LOGGER.info("phase: %s (%s)", build.current_phase.value, build.status.value)

        yield build

    if build.status is not BuildStatus.succeeded:
        raise RuntimeError(f"CodeBuild build ({build_id}) is {build.status.value}")
    LOGGER.debug(
        "start: %s | end: %s | elapsed: %s",
        build.start_time,
        build.end_time,
        build.duration_in_seconds,
    )


SPEC_TYPE = Dict[str, Union[float, Dict[str, Dict[str, Union[List[str], Dict[str, float]]]]]]


def generate_spec(
    stack_outputs: Dict[str, str],
    cmds_install: Optional[List[str]] = None,
    cmds_pre: Optional[List[str]] = None,
    cmds_build: Optional[List[str]] = None,
    cmds_post: Optional[List[str]] = None,
) -> SPEC_TYPE:
    """Generate a BuildSpec for a CodeBuild execution

    Parameters
    ----------
    stack_outputs : Dict[str, str]
        The CloudFormation Stack Outputs from the Seedkit Stack where the CodeBuild Project was created
    cmds_install : Optional[List[str]], optional
        Additional commands to run during the Install phase of the CodeBuild execution, by default None
    cmds_pre : Optional[List[str]], optional
        Additional commands to run during the PreBuild phase of the CodeBuild execution, by default None
    cmds_build : Optional[List[str]], optional
        Additional commands to run during the Build phase of the CodeBuild execution, by default None
    cmds_post : Optional[List[str]], optional
        Additional commands to run during the PostBuild phase of the CodeBuild execution, by default None

    Returns
    -------
    SPEC_TYPE
        A CodeBuild BuildSpec
    """
    pre: List[str] = [] if cmds_pre is None else cmds_pre
    build: List[str] = [] if cmds_build is None else cmds_build
    post: List[str] = [] if cmds_post is None else cmds_post
    install = [
        (
            "aws codeartifact login --tool pip "
            f"--domain {stack_outputs['CodeArtifactDomain']} "
            f"--repository {stack_outputs['CodeArtifactRepository']}"
        ),
        "/var/scripts/retrieve_docker_creds.py && echo 'Docker logins successful' || echo 'Docker logins failed'",
    ]

    if cmds_install is not None:
        install += cmds_install

    return_spec: SPEC_TYPE = {
        "version": 0.2,
        "phases": {
            "install": {
                "runtime-versions": {"python": 3.7, "nodejs": 12, "docker": 19},
                "commands": install,
            },
            "pre_build": {"commands": pre},
            "build": {"commands": build},
            "post_build": {"commands": post},
        },
    }
    LOGGER.debug(return_spec)
    return return_spec
