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
import time
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Tuple, Union, overload

import boto3
import botocore

from aws_codeseeder import LOGGER, __version__, _classes

if TYPE_CHECKING:
    from boto3.resources.base import ServiceResource
    from botocore.client import BaseClient
    from mypy_boto3_cloudformation import CloudFormationClient
    from mypy_boto3_cloudwatch import CloudWatchClient
    from mypy_boto3_codebuild import CodeBuildClient
    from mypy_boto3_iam import IAMClient, IAMServiceResource
    from mypy_boto3_logs import CloudWatchLogsClient
    from mypy_boto3_s3 import S3Client, S3ServiceResource
    from mypy_boto3_sts import STSClient

_session_singleton: _classes.SessionSingleton = _classes.SessionSingleton()


def _get_botocore_config() -> botocore.config.Config:
    return botocore.config.Config(
        retries={"max_attempts": 5},
        connect_timeout=10,
        max_pool_connections=10,
        user_agent_extra=f"aws-codeseeder/{__version__}",
    )


@overload
def boto3_client(
    service_name: Literal["cloudformation"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "CloudFormationClient": ...


@overload
def boto3_client(
    service_name: Literal["cloudwatch"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "CloudWatchClient": ...


@overload
def boto3_client(
    service_name: Literal["codebuild"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "CodeBuildClient": ...


@overload
def boto3_client(
    service_name: Literal["iam"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "IAMClient": ...


@overload
def boto3_client(
    service_name: Literal["logs"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "CloudWatchLogsClient": ...


@overload
def boto3_client(
    service_name: Literal["s3"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "S3Client": ...


@overload
def boto3_client(
    service_name: Literal["sts"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "STSClient": ...


@overload
def boto3_client(
    service_name: str,
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "BaseClient": ...


def boto3_client(
    service_name: str, session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = None
) -> "BaseClient":
    if session is None:
        session = _session_singleton.value if _session_singleton.value is not None else boto3.Session()
    elif callable(session):
        session = session()

    return session.client(service_name=service_name, use_ssl=True, config=_get_botocore_config())  # type: ignore[call-overload,no-any-return]


@overload
def boto3_resource(
    service_name: Literal["iam"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "IAMServiceResource": ...


@overload
def boto3_resource(
    service_name: Literal["s3"],
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "S3ServiceResource": ...


@overload
def boto3_resource(
    service_name: str,
    session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = ...,
) -> "ServiceResource": ...


def boto3_resource(
    service_name: str, session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = None
) -> "ServiceResource":
    if session is None:
        session = _session_singleton.value if _session_singleton.value is not None else boto3.Session()
    elif callable(session):
        session = session()

    return session.resource(service_name=service_name, use_ssl=True, config=_get_botocore_config())  # type: ignore[call-overload,no-any-return]


def set_boto3_session(session: boto3.Session) -> None:
    _session_singleton.value = session


def get_region(session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = None) -> str:
    if session is None:
        session = _session_singleton.value if _session_singleton.value is not None else boto3.Session()
    elif callable(session):
        session = session()

    if session.region_name is None:
        raise ValueError("It is not possible to infer AWS REGION from your environment.")
    return str(session.region_name)


def get_sts_info(session: Optional[Union[Callable[[], boto3.Session], boto3.Session]] = None) -> Tuple[str, str, str]:
    """
    get_sts_info _summary_

    Parameters
    ----------
    session : Optional[Union[Callable[[], boto3.Session], boto3.Session]], optional
        _description_, by default None

    Returns
    -------
    Tuple[str, str, str]
        returns the account id, role arn, and aws partition of the session provided
    """
    sts_info = boto3_client(service_name="sts", session=session).get_caller_identity()
    return (sts_info["Account"], sts_info["Arn"], sts_info["Arn"].split(":")[1])


def try_it(
    f: Callable[..., Any],
    ex: Any,
    base: float = 1.0,
    max_num_tries: int = 3,
    **kwargs: Any,
) -> Any:
    """Run function with decorrelated Jitter.

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    delay: float = base
    for i in range(max_num_tries):
        try:
            return f(**kwargs)
        except ex as exception:
            if i == (max_num_tries - 1):
                raise exception
            delay = random.uniform(base, delay * 3)
            LOGGER.error(
                "Retrying %s | Fail number %s/%s | Exception: %s",
                f,
                i + 1,
                max_num_tries,
                exception,
            )
            time.sleep(delay)
